from sqlalchemy import ForeignKey, Column, Integer, String, MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

engine = create_engine("sqlite:///freebies.db")
Session = sessionmaker(bind=engine)
session = Session()

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    founding_year = Column(Integer())
    dev_id = Column(Integer(), ForeignKey("devs.id"))

    freebie = relationship("Freebie", backref=backref("company"))
    dev = association_proxy("freebie", "dev")

    def give_freebie(self, dev, item_name, value):
        new_freebie = Freebie(item_name=item_name, value=value)
        new_freebie.company = self
        new_freebie.dev = dev
        session.commit()

    @classmethod
    def oldest_company(cls):
        return session.query(cls.name).order_by(cls.founding_year).first()

    def __repr__(self):
        return f"<Company {self.name}>"


class Dev(Base):
    __tablename__ = "devs"

    id = Column(Integer(), primary_key=True)
    name = Column(String())

    company_id = Column(Integer(), ForeignKey("companies.id"))

    freebie = relationship("Freebie", backref=backref("dev"))
    companies = association_proxy("freebie", "company")

    def received_one(self, item_name):
        dev_items = [self.item_name for self in self.freebie]
        return item_name in dev_items

    def give_away(self, dev, freebie):
        if freebie in self.freebie:
            self.freebie.remove(freebie)
            dev.freebie.append(freebie)
            session.commit()
        else:
            print(f"{self.name} doesn't own a {freebie.item_name} to give away.")

    def __repr__(self):
        return f"<Dev {self.name}>"


class Freebie(Base):
    __tablename__ = "freebies"

    id = Column(Integer(), primary_key=True)
    item_name = Column(String())
    value = Column(Integer())

    dev_id = Column(Integer(), ForeignKey("devs.id"))
    company_id = Column(Integer(), ForeignKey("companies.id"))

    def print_details(self):
        return f"{self.dev.name} owns a {self.item_name} from {self.company.name}"


freebie = session.query(Freebie).all()[36]
dev = session.query(Dev).all()[0]
dev2 = session.query(Dev).all()[1]
dev.give_away(dev2, freebie)
