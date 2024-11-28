from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.utils.config_parser.config_parser import parse_config


Base = declarative_base()

class InputParameters(Base):
    __tablename__ = "input_parameters"
    id = Column(Integer, primary_key = True)
    seq_id = Column(String)
    chr = Column(String)
    variant_pos = Column(String)
    target = Column(String)
    flanks = Column(String)
    num_ret = Column(Integer)
    hash = Column(String, unique = True)

class PrimerPairs(Base):
    __tablename__ = "primer_pairs"
    id = Column(Integer, primary_key = True)
    input_parameter_id = Column(Integer, ForeignKey("input_parameters.id"))

    left_start_pos = Column(String)
    left_end_pos = Column(String)

    right_start_pos = Column(String)
    right_end_pos = Column(String)

    left_primer = Column(String)
    right_primer = Column(String)

    left_tm = Column(String)
    left_gc = Column(String)

    right_tm = Column(String)
    right_gc = Column(String)


    MedvarDb_forward = Column(String)
    MedvarDb_reverse = Column(String)

    thousandG_forward = Column(String)
    thousandG_reverse = Column(String)

    CRDB_forward = Column(String)
    CRDB_reverse = Column(String)

    gnomad_forward = Column(String)
    gnomad_reverse = Column(String)

    left_cord_start = Column(String)
    left_cord_end = Column(String)

    right_cord_start = Column(String)
    right_cord_end = Column(String)



def get_session():
    config = parse_config('primerDb')
    db_url = config['db_url']

    engine = create_engine(db_url)

    Base.metadata.create_all(engine)

    session = sessionmaker(bind = engine)
    return session()


# session = get_session()

# input_params = InputParameters(seq_id = "CHR1", chr = 'chr1', variant_pos = '15529554', target = '900,200', num_ret = 5, hash = "f6df2ebe17c2cb9cb56db8893c546006")
# session.add(input_params)
# session.commit()



# primer_pair = PrimerPairs(input_parameter_id=input_params.id, primer_forward="AAA...", primer_reverse="TTT...")
# session.add(primer_pair)
# session.commit()

# primer_pairs = session.query(PrimerPairs).filter(PrimerPairs.id == 2)
#
# res = session.query(PrimerPairs, InputParameters).filter(InputParameters.id == 2)



