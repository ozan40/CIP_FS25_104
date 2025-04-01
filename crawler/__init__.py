# mit diesem __all__ sage ich, in diesem Package habe ich diese Files und damit erlaube ich,
# dass ich diese importieren kann.
__all__ = ["CrawledCar","CarsFetcher","WebAutomation", "CarFetcher"]

# Damit das alles klappt, muss ich hier im __init__ file noch sage, hey importiere doch dieses Modul.
# Python betrachtet also nicht diese __all__ variable, sondern wir müssen noch zusätzlichi import Befehle platzieren,
from .CarsFetcher import CarsFetcher
from .CrawledCar import CrawledCar
from .Auto_de_scraper import WebAutomation, CarFetcher