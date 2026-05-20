
import json
import os

def refactor():
    path = "c:/Users/augus/PycharmProjects/MyFirstGui/json_db/stamford/text_horologion.json"
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updates = {
        "horologion.blessing_common": {
            "title": "Blessing",
            "content": "Priest: Blessed be our God, always, now and for ever and ever.\nChoir: Amen.",
            "source": "Stamford Horologion (Inferred)"
        },
        "horologion.glory_to_holy": {
            "title": "Exclamation",
            "content": "Priest: Glory to the holy, consubstantial, life-creating and undivided Trinity, always, now and for ever and ever.\nChoir: Amen.",
            "source": "Stamford Horologion (Inferred)"
        },
        "horologion.trisagion_block": {
            "title": "Introductory Prayers",
            "content": "Holy God, Holy Mighty, Holy Immortal, have mercy on us. (3x)\nGlory be to the Father and to the Son and to the Holy Spirit, now and for ever and ever. Amen.\nTrinity most holy, have mercy on us. Cleanse us of our sins, O Lord; pardon our transgressions, O Master; look upon our weaknesses and heal them, O Holy One; for the sake of Your name.\nLord, have mercy. (3x)\nGlory be to the Father and to the Son and to the Holy Spirit, now and for ever and ever. Amen.\nOur Father, Who art in heaven, hallowed be Thy name. Thy kingdom come. Thy will be done on earth as it is in heaven. Give us this day our daily bread, and forgive us our trespasses as we forgive those who trespass against us. And lead us not into temptation, but deliver us from evil.\nPriest: For Thine is the kingdom and the power and the glory, Father, Son, and Holy Spirit, now and for ever and ever.\nChoir: Amen.\nLord, have mercy. (12x)\nGlory be to the Father and to the Son and to the Holy Spirit, now and for ever and ever. Amen.\nCome, let us adore the King, our God.\nCome, let us adore Christ, the King and our God.\nCome, let us adore and bow down to the only Lord Jesus Christ, the King and our God.",
            "source": "Stamford Horologion (Common)"
        },
        "horologion.psalm_19": {
            "title": "Psalm 19",
            "content": "May the Lord hear you in the day of distress;* may the name of the God of Jacob defend you.\nMay He send you help from the sanctuary* and from Zion may He sustain you.\nMay He remember all your sacrifices,* and may your whole burnt offering be honored.\nMay He give you what your heart desires* and fulfill all your plans.\nWe shall rejoice in your salvation* and in the name of our God we shall be great.\nMay the Lord fulfill all your petitions.* Now I know that the Lord has saved His anointed.\nHe will hear him from His holy heaven;* in His right hand is the power of salvation.\nSome trust in chariots and some in horses,* but we will call upon the name of the Lord our God.\nThey have collapsed and fallen,* but we have risen and stand upright.\nO Lord, save the king* and hear us on the day we call upon You.",
            "source": "Stamford Horologion (Common)"
        },
        "horologion.psalm_20": {
            "title": "Psalm 20",
            "content": "In Your strength, O Lord, the king rejoices,* in Your salvation he is glad indeed.\nYou have given him his heart’s desire* and have not withheld the request of his lips.\nFor You established him with blessings of goodness;* You placed a crown of precious stones/gold upon his head.\nHe asked You for life and You gave it to him,* length of days forever and ever.\nGreat is his glory in Your salvation;* glory and majesty You lay upon him.\nFor You will give him a blessing forever and ever;* You will gladden him with the joy of Your face.\nFor the king trusts in the Lord,* and through the mercy of the Most High he shall not be moved.\nMay Your hand reach all Your enemies;* may Your right hand find all who hate You.\nYou shall make them like a fiery furnace* when Your face appears.\nThe Lord will destroy them in His anger,* and fire will devour them.\nYou will wipe out their offspring from the earth* and their seed from among the children of men.\nFor they plotted evil against You,* they devised purposes they could not fulfill.\nFor You will put them to flight;* You will ready Your arrows against their face.\nBe exalted, O Lord, in Your strength;* we will sing and praise Your might.",
            "source": "Stamford Horologion (Common)"
        }
    }

    for key, item in updates.items():
        data[key] = item
        print(f"Added/Updated {key}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Fixed texts injection complete.")

if __name__ == "__main__":
    refactor()
