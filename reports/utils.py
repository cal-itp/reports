from siuba import *
from siuba.sql import LazyTbl
from siuba.dply import vector as vec

from sqlalchemy import create_engine

# limit at 5 Gb
engine = create_engine("bigquery://cal-itp-data-infra/?maximum_bytes_billed=5000000000")

class AutoTable:
    def __init__(self, engine, table_formatter = None, table_filter = None):
        self._engine = engine
        self._table_names = self._engine.table_names()
        
        mappings = {}
        for name in self._table_names:
            if table_filter is not None and not table_filter(name):
                continue
                
            fmt_name = table_formatter(name)
            if fmt_name in mappings:
                raise Exception("multiple tables w/ formatted name: %s" %fmt_name)
            mappings[fmt_name] = name
        
        self._attach_mappings(mappings)
        
    def _attach_mappings(self, mappings):
        for k, v in mappings.items():
            loader = lambda self: self._load_table
            setattr(self, k, self._table_factory(v))
    
    def _table_factory(self, table_name):
        def loader():
            return self._load_table(table_name)
        
        return loader
    
    def _load_table(self, table_name):
        return LazyTbl(self._engine, table_name)
        

tbl = AutoTable(
    engine,
    lambda s: s.replace(".", "_").replace("test_", ""),
    lambda s: "test_" not in s and "__staging" not in s
)
