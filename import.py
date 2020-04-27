import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://kklffhyzdcaqff:f48cea3a53ea8c42f850a4237883371744d1e90e3b03b06c5edf26c8a5361cb9@ec2-34-202-7-83.compute-1.amazonaws.com:5432/df9ea9a04nkdmp", pool_pre_ping=True)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for ISBN, Title, Author, Year in reader:
        db.execute("INSERT INTO bookinfo VALUES(:ISBN,:Title,:Author,:Year)",{"ISBN":ISBN,"Title":Title,"Author":Author,"Year":Year})
        print(f"Added {Author},{Title}")
    db.commit()
if __name__ == "__main__":
    main()
