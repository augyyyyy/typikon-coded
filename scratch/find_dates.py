import sys
import os
import datetime

sys.path.append(r"c:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded")

from engine import RuthenianEngine

engine = RuthenianEngine()

for year in range(2025, 2035):
    # To get Pascha, we can probe Jan 1st and do the math
    ctx = engine.get_liturgical_context(datetime.date(year, 1, 1))
    offset = ctx["pascha_offset"]
    pascha = datetime.date(year, 1, 1) - datetime.timedelta(days=offset)
    print(f"Year {year}: Pascha is {pascha}")
    
    # Check March 25 (Annunciation)
    annun = datetime.date(year, 3, 25)
    days_to_pascha = (pascha - annun).days
    if days_to_pascha in [0, 1, 2, 3, 4, 5, 6, 7]:
        print(f"  -> Annunciation is {days_to_pascha} days before Pascha (Holy Week/Pascha!)")

    # Check Feb 2 (Meeting)
    meeting = datetime.date(year, 2, 2)
    days_to_pascha_feb2 = (pascha - meeting).days
    if 49 <= days_to_pascha_feb2 <= 70 and meeting.weekday() == 6:
        print(f"  -> Meeting of the Lord is on a Sunday in the Triodion! ({days_to_pascha_feb2} days before Pascha)")

    # Check Dec 24 (Christmas Eve) falling on Sunday
    dec24 = datetime.date(year, 12, 24)
    if dec24.weekday() == 6:
        print(f"  -> Christmas Eve is on a Sunday!")

    # Check Sept 14 (Exaltation of the Cross) falling on Sunday
    sept14 = datetime.date(year, 9, 14)
    if sept14.weekday() == 6:
        print(f"  -> Exaltation of the Cross is on a Sunday!")

    # Check Feb 24 (Finding of Head of John Baptist)
    feb24 = datetime.date(year, 2, 24)
    days_to_pascha_feb24 = (pascha - feb24).days
    if 49 <= days_to_pascha_feb24 <= 70 and feb24.weekday() == 6:
        print(f"  -> Finding of the Head of John the Baptist is on a Sunday in the Triodion! ({days_to_pascha_feb24} days before Pascha)")
