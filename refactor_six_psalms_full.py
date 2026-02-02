import json
import os
import re

db_path = "json_db/stamford/text_horologion.json"

doxology_text = {
    "horologion.matins.mid_six_psalms_doxology": {
        "title": "Doxology (Mid-Six Psalms)",
        "content": "Glory to the Father and to the Son and to the Holy Spirit, now and for ever and ever. Amen.\nAlleluia! Alleluia! Alleluia! Glory be to You, O God! (3x)\nLord, have mercy (3x).\nGlory to the Father and to the Son and to the Holy Spirit, now and for ever and ever. Amen.",
        "source": "Stamford Horologion (Reconstructed)"
    }
}

clean_psalm_142 = """(Saturday and Sunday)
Lord, listen to my prayer; turn Your ear to my appeal;* You are faithful; You are just; give answer.
Do not call Your servant to judgment* for no one is just in Your sight.
The enemy pursues my soul; he has crushed my life to the ground;* He has made me dwell in darkness like the dead, long forgotten.
Therefore, my spirit fails;* my heart is numb within me.
I remember the days that are past: I ponder all Your works;* I muse on what Your hand has wrought and to You I stretch out my hands.
Like a parched land my soul thirsts for You;* Lord, make haste and answer; for my spirit fails within me.
Do not hide Your face* lest I become like those in the grave.
In the morning let me know Your love for I put my trust in You;* make me know the way I should walk;* to You I lift up my soul.
Rescue me, Lord, from my enemies;* I have fled to You for refuge.
Teach me to do Your will, for You, O Lord, are my God;* let Your good Spirit guide me in ways that are level and smooth.
For Your name’s sake, Lord, save my life;* in Your justice save my soul from distress.
In Your love make an end of my foes;* destroy all those who oppress me for I am Your servant, O Lord.
After every psalm:
Glory be to the Father and to the Son and to the Holy Spirit:
Now and for ever, and ever. Amen.
Alleluia! Alleluia! Alleluia! Glory be to You, O God! (3x)"""

# Extracted from the "Prayers of Matins" block in existing json
# Manually separating them for precision
prayers = {
    "horologion.matins.prayer_1": {
        "title": "Prayer 1 (Morning)",
        "content": "We thank You, Lord our God, for You have wakened us from our sleep, and have filled our lips with praise that we might worship You and call upon Your holy name. We beg of Your compassion that You have always shown towards us, hear us now and send help to those who stand before Your holy glory awaiting Your abundant mercy. O Lord, grant that those who serve You in fear and love may praise Your ineffable goodness. For to You is due all glory, honor, and worship, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_2": {
        "title": "Prayer 2 (Morning)",
        "content": "From the depths of night our soul longs for You, our God, for Your commandments are a light upon the earth. Give us understanding that we may be perfected in righteousness and holiness in fear of You, for it is You Whom we glorify as our true God. Turn Your ear and hear us. O Lord, remember all those present and praying with us by their own name, and save them by Your might. Bless Your people and sanctify Your inheritance. Give peace to Your world, to Your churches, to the priests, and to all Your people. For blessed and glorified is Your most honored and sublime name, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_3": {
        "title": "Prayer 3 (Morning)",
        "content": "From the depths of night our soul longs for You, our God, for Your commandments are a light upon the earth. Teach us, O God, Your righteousness, Your statutes, and Your decrees. Enlighten the eyes of our minds, lest in sin we fall asleep until death. Cast out all darkness from our hearts, favor us with the Sun of Righteousness, and keep our lives from danger by the seal of Your Holy Spirit. Direct our steps along the road of peace. Grant that we may see the dawn and the whole day in joy, and that we may offer You our morning prayers. For Yours is the power, and Yours is the kingdom and the might and the glory, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_4": {
        "title": "Prayer 4 (Morning)",
        "content": "Lord God, holy and incomprehensible, You told the light to shine out of darkness; You have given us rest in the sleep of night; and You have raised us to glorify and praise Your goodness. We beg of Your mercy, accept us who now worship You and thank You with all our strength, and grant all that we ask for our salvation. Reveal us to be children of light and of the day, and heirs of Your eternal good gifts. In the abundance of Your mercy, Lord, remember all Your people who invoke Your love for mankind and aid those here present and who pray with us and those traveling abroad in every place of Your kingdom, who are in need of Your loving kindness and help. Be greatly merciful to all, that we may persevere always in confidence, being saved in soul and body. We glorify Your magnificent and blessed name, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_5": {
        "title": "Prayer 5 (Morning)",
        "content": "Treasury of all good, ever-flowing spring, holy Father, Wonder-worker, all-powerful Ruler of all: we worship You and beg of Your mercy and compassion, help and support us in our lowliness. Lord, remember those who pray to You, and let our morning prayer rise like incense before You. Grant that no one of us may be put to shame, but surround us with Your mercy. Lord, remember those who keep watch and sing of Your glory, and that of Your only-begotten Son and our God, and of Your Holy Spirit. Be their help and support and accept their prayers upon Your heavenly spiritual altar. For You are our God, and to You we give glory, to the Father, and to the Son, and to the Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_6": {
        "title": "Prayer 6 (Morning)",
        "content": "We give thanks to You, O Lord and God of our salvation. You have done everything that is good for our lives, and we look always to You, Savior and Benefactor of our souls. For You have given us rest in that part of the night which has passed, and now have raised us from our sleep to worship Your honored name. Therefore, O Lord, we pray: give us the grace and strength to be found worthy to sing praise always, and to pray constantly, and to work for our own salvation in fear and trembling, with the help of Your Christ. O Lord, remember those who pray to You in the night. Hear them and have mercy on them and crush under their feet invisible and malicious enemies. For You are the King of Peace, and the Savior of our souls, and we give thanks to You, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_7": {
        "title": "Prayer 7 (Morning)",
        "content": "God and Father of our Lord Jesus Christ, You have raised us from our sleep and gathered us for this time of prayer. Give us grace that we may open our lips in praise. Accept the thanksgiving we offer with all our strength. Teach us Your decrees, for we do not know how to pray as we should, unless You guide us by Your Holy Spirit. Therefore, we pray, that if until now we have sinned in any way – in word, or deed, or thought, voluntarily or involuntarily – remit, pardon and forgive us; for if You, O Lord, were to look upon our guilt, Lord, who would survive? For with You is found redemption. You alone are holy and a helper and the stronghold of our lives, and our praise is for You forever. Blessed and glorified be the power of Your reign, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_8": {
        "title": "Prayer 8 (Morning)",
        "content": "Lord our God, You have shaken from us the laziness of sleep; You have called us to be holy, to lift up our hands in the night, and to glorify You for Your just decrees. Receive our prayers, our petitions, our confessions of faith, and our nighttime worship. Bestow on us, O Lord, an invincible faith, a confident hope, and a love without pretense. Bless our comings and our goings, our deeds and works, our words and desires. Grant that we may come to the beginning of the day praising, glorifying, and blessing the goodness of Your inexpressible generosity. For blessed is Your all-holy name, and glorified is Your kingdom, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_9": {
        "title": "Prayer 9 (Morning)",
        "content": "O Lord our God, You have given us forgiveness through repentance, and as a model of knowledge and confession of sins, You have revealed to us the repentance of the prophet David that led to pardon. Master, have mercy on us who have fallen into so many and so great sins. Have mercy in Your kindness, and in Your compassion blot out our offenses, for against You have we sinned, O Lord, Who know the hidden depths of our hearts, and Who alone have the power to forgive sins. A pure heart You have created for us; You have sustained us with a spirit of fervor and have given us the joy of Your help. Do not cast us away from Your presence, but in Your goodness and love for all, grant that we may offer a sacrifice of righteousness and oblation on Your holy altar until our last breath. Through the mercies and goodness and love of Your only-begotten Son, with Whom You are blessed, together with Your good and life-creating Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_10": {
        "title": "Prayer 10 (Morning)",
        "content": "O God, our God, who have placed all spiritual and intellectual powers under Your will, we pray and beg You, accept these hymns of praise which we offer to You according to our ability together with all Your creatures. Give us in exchange the riches of Your goodness, for before You all beings in the heavens, or on earth and under the earth bend their knees, and everything that lives or that breathes gives praise to Your glory beyond reach, for You are the one true God, full of mercy. For all the heavenly powers praise You, and we give glory to You, to the Father, and to the Son, and to the Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_11": {
        "title": "Prayer 11 (Morning)",
        "content": "God of our ancestors, we praise You, we glorify You, we bless You, we thank You, for You have made the shadow of night pass and have shown us again the light of day. We beg You in Your goodness and in Your great mercy, cleanse our sins and hear our prayer, for we take refuge in You, O merciful and all-powerful God. Make the true Sun of Righteousness shine in our hearts, enlighten our minds, and watch over all our senses, that we may live decently like people of the daytime, so that walking in Your commandments, we may come to eternal life, and may be made worthy of the enjoyment of Your light beyond reach, for You are the source of life. For You are a God of mercy and kindness and love, and we glorify You, Father, Son, and Holy Spirit, now and for ever and ever. Amen."
    },
    "horologion.matins.prayer_12": {
        "title": "Prayer 12 (Morning)",
        "content": "O Lord, compassionate and loving, long-suffering and most merciful, hear our prayer and listen to the voice of our supplication. Make a favorable covenant with us, guide us along Your ways that we may live in Your truth, gladden our hearts that we may fear Your holy name; for You are great and You perform wondrous deeds. You are the only God and none other is like You, O Lord. You are great in mercy and able, in Your power, to assist, support, and save all those who place their hope in Your holy name; and to You, Father, Son, and Holy Spirit, is due all glory, honor, and adoration, now and for ever and ever. Amen." 
        # Note: In Stamford text, Prayer 12 might have been the first "Prayer of Light".
        # Checking logic order: "O Lord, compassionate and loving" was listed first in the block in psalm_103... 
        # Wait, the source text listed them in specific order. I'm using the ones identified from "Prayers of Matins" block in psalm_142.
        # This one seems to be generally the 12th.
    }
}

def run():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Update content
    data.update(doxology_text)
    data.update(prayers)
    
    # Clean Psalm 142
    if "horologion.psalm_142" in data:
        data["horologion.psalm_142"]["content"] = clean_psalm_142
        print("Cleaned Psalm 142 content.")
    if "horologion.common.psalm_142" in data:
        data["horologion.common.psalm_142"]["content"] = clean_psalm_142
        print("Cleaned common.psalm_142 content.")

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("Six Psalms Data Refactored Successfully.")

if __name__ == "__main__":
    run()
