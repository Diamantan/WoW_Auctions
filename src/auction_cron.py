# Auctioncron.py
# Gets new auctions, processes them and updates the database. To be ran as a cron job.

import models
import logging
import battlenet
import sys
import time
import multiprocessing
import os
import json
import datetime
from sqlalchemy.orm.exc import NoResultFound

#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def log(message):
    # Quick and dirty.
    sys.stdout.write("%s: %s\n"%(time.asctime(), message))

def GrabItemInfo(data):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    r = api.get_item(data["item"])
    if r:
        r._auctionID = data["auc"]
        sys.stdout.write(".")
        return r
    else:
        sys.stdout.write("!")
        
def HandleRealm(realm):
    api = battlenet.BattleNetApi(log)
    
    log("Connecting to the database...")
    session = models.Session()
    log("Connection successful. Parsing...")
    
    log(" - Realm: %s"%realm)
    try:
        db_realm = session.query(models.Realm).filter(models.Realm.slug == realm.slug).one()
    except Exception:
        db_realm = models.Realm(realm.name, realm.slug)
        session.add(db_realm)
        session.commit()
    
    log("  - DB LastModified: %s"%time.ctime(db_realm.lastupdate))
    
    for i in xrange(5):
        try:
            lastModified, auctions = api.get_auction(realm.slug, db_realm.lastupdate)
            break
        except Exception:
            if i == 4:
                log("   - Not attempting again, returning.")
                return
            log("   - Attempting again...")
    
    if (lastModified, auctions) == (None, None):
        log("   - Skipping auctions for realm %s"%realm)
        return
    
    log("  - LastModified: %s"%(time.ctime(lastModified / 1000)))
    

    db_realm.auction_count = 0
            
    for key in ("alliance","horde","neutral"):
        auc = auctions[key]["auctions"]
        db_realm.auction_count+=len(auc)
        
        _json_path = "auction_cache/%s_%s.json"%(db_realm.slug, key)
            
        log("   - Found %s auctions for faction %s"%(len(auc), key))
        auc_ids = set([auction_data["auc"] for auction_data in auc])
        
        if os.path.exists(_json_path): # We have the previous shit on record
            with open(_json_path,"r") as pd:
                try:
                    previous_ids = json.load(pd)
                except ValueError:
                    log("    - Error decoding JSON document %s! Removing"%_json_path)
                    os.remove(_json_path)
                
                else:
                    new_ids = auc_ids - set(previous_ids)
                    log("    - Found %s new auctions"%len(new_ids))
                    
                    new_item_ids = [t["item"] for t in auc if t["auc"] in new_ids]
                    if not len(new_item_ids):
                        log("     - Passing...")
                        continue
                    query = session.query(models.Price).filter(models.Price.day==datetime.datetime.now().date()) \
                                                                   .filter(models.Price.realm==db_realm) \
                                                                   .filter(models.Price.item_id.in_(new_item_ids)) \
                                                                   .filter(models.Price.faction==key)
                    price_objects = {p.item_id:p for p in query.all()}
                    to_add = []
                    
                    for auction in auc:
                        if auction["auc"] in new_ids:
                            # We got a new item yo
                            '''try:
                                item_db = session.query(models.Item).filter(models.Item.id == auction["item"]).one()
                                #log("    - Item ID %s exists, not fetching"%auction["item"])
                            except Exception:
                                log("    - Item ID %s does not exist. Fetching and adding"%auction["item"])
                                _item = api.get_item(auction["item"])
                                if not _item:
                                    log("     - Cannot fetch item id %s!"%auction["item"])
                                else:
                                    item_db = models.Item(auction["item"], _item.name, _item.icon, _item.description,
                                                          _item.buyPrice, _item.sellPrice, _item.quality, _item.itemLevel)
                                    session.add(item_db)
                                    #session.commit()'''
                                    
                            userauction = models.UserAuction(auction["owner"], auction["item"]) #TODO: Verify this
                            to_add.append(userauction)
                            
                            # Lets see if we have a Price already
                            if auction["item"] in price_objects:
                                price_db = price_objects[auction["item"]]
                            else:
                                #price = models.Price()
                                price_db = models.Price(datetime.datetime.now().date(), db_realm, auction["item"],
                                                        0, 0, 0,
                                                        key)
                                price_objects[auction["item"]] = price_db
                                
                            price_db.quantity+=auction["quantity"]
                            if price_db.average_counter > 0:
                                price_db.bid = ((price_db.bid * price_db.average_counter) + auction["bid"]) / price_db.average_counter + 1
                                price_db.buyout = ((price_db.buyout * price_db.average_counter) + auction["buyout"]) / price_db.average_counter + 1
                                price_db.average_counter+=1
                            else:
                                price_db.bid = auction["bid"]
                                price_db.buyout = auction["buyout"]
                                price_db.average_counter = 1
                            to_add.append(price_db)
                            
                    session.add_all(to_add)
                    session.commit()
        
        else:
            log("    - No previous dump found, dumping current record.")
        
        with open(_json_path, "w") as fd:
            json.dump(list(auc_ids), fd)
    
    db_realm.lastupdate = lastModified / 1000
    session.add(db_realm)
    session.commit()
    log("   - Finished realm %s"%db_realm.slug)

if __name__ == "__main__":
    
    if not os.path.exists("auction_cache"):
        os.mkdir("auction_cache")

    log("Spinning up processing pools...")
    realm_pool = multiprocessing.Pool(10)
    
    api = battlenet.BattleNetApi(log)
    
    log("Getting realm list...")
    realms = api.get_realms()
    log("Retrieved %s realms, sending to the realm pool"%len(realms))
    
    realm_pool.map(HandleRealm, realms)
    #for realm in realms:
    #    HandleRealm(realm)