from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Date, ForeignKey, Enum, create_engine, func
from sqlalchemy import schema
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgresql+psycopg2://wowauction:password@localhost:5432/wow_auctions",
                       pool_size=20, isolation_level="REPEATABLE_READ")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Realm(Base):
    __tablename__ = "realms"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, index=True)
    slug = Column(String(200), unique=True, index=True)
    lastupdate  = Column(Integer)
    auction_count = Column(Integer)
    
    def __init__(self, name, slug):
        self.name = name
        self.slug = slug
        self.lastupdate = 0
    
    def __repr__(self):
        return "<Realm(%s, %s, %s)>"%(self.name, self.slug, self.lastupdate)
    

class Item(Base):
    __tablename__ = "item"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    icon = Column(String(250))
    description = Column(String)
    
    buyprice = Column(BigInteger)
    sellprice = Column(BigInteger)
    quality = Column(Integer)
    level = Column(Integer)

    def __init__(self, id, name, icon, description, buyprice, sellprice, quality, level):
        self.id = id
        self.name = name
        self.icon = icon
        self.description = description
        self.sellprice = sellprice
        self.buyprice = buyprice
        self.quality = quality
        self.level = level
        
    def __repr__(self):
        return "<Item(%s,%s)>"%(self.name, self.icon)
    
    def get_icon(self):
        return "http://us.media.blizzard.com/wow/icons/56/%s.jpg"%self.icon
    

class UserAuction(Base):
    __tablename__ = "userauctions"
    
    id = Column(Integer, primary_key=True)
    owner = Column(String)
    added = Column(DateTime, default=func.now())
    
    item_id = Column(Integer)#, ForeignKey("item.id"))
    #item = relationship("Item", backref=backref("sellers", order_by=-added))
    
    def __init__(self, owner, item):
        self.owner = owner
        self.item = item


#class Faction(Base):
#    __tablename__ = "factions"
#    id = Column(Integer, primary_key=True)
#    name = Column(String(8))


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (schema.PrimaryKeyConstraint('realm_id','item_id','faction','day'),)
    #(Index("price_finder", 'day', 'realm_id', 'item_id', 'faction'),)
    
    #id = Column(Integer, primary_key=True)
    
    day = Column(Date, default=func.now(), primary_key=True)
    
    realm_id = Column(Integer, ForeignKey("realms.id"), primary_key=True)
    realm = relationship("Realm")
    
    item_id = Column(Integer, primary_key=True)#, ForeignKey("item.id"))
    #item = relationship("Item", backref=backref("prices", order_by=-day, primaryjoin = item_id == Item.id))
    
    buyout   = Column(BigInteger) # Average buyout
    bid      = Column(BigInteger) # Average bid
    quantity = Column(Integer) # Number of items seen this day
    average_counter = Column(Integer)
    
    faction = Column(Enum("neutral","horde","alliance", name="faction_enum"), primary_key=True) # Neutral, Horde, Alliance
    
    
    
    def __init__(self, day, realm, item, buyout, bid, quantity, faction):
        self.day = day
        self.realm = realm
        self.item_id = item
        self.buyout = buyout
        self.bid = bid
        self.quantity = quantity
        self.faction = faction
        self.average_counter = 0

Base.metadata.create_all(engine)