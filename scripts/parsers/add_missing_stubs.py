#!/usr/bin/env python3
"""
Create stub entries for all missing keys required by struct files.
Uses master key registry as source of truth.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAMFORD_DIR = os.path.join(BASE_DIR, "json_db", "stamford")

# Missing keys organized by which text file they should go in
MISSING_KEYS = {
    "text_horologion.json": [
        ("horologion.axion_estin", "It is truly meet..."),
        ("horologion.blessed_be_name_3x", "Blessed be the Name of the Lord..."),
        ("horologion.blessing_common", "Blessed is our God..."),
        ("horologion.blessing_vigil", "Glory to the holy..."),
        ("horologion.creed", "I believe in one God..."),
        ("horologion.dismissal_full", "May Christ our true God..."),
        ("horologion.dismissal_great", "The great dismissal"),
        ("horologion.dismissal_great_compline_standard", "Compline dismissal"),
        ("horologion.dismissal_great_friday", "Good Friday dismissal"),
        ("horologion.dismissal_great_saturday", "Holy Saturday dismissal"),
        ("horologion.dismissal_lenten", "Lenten dismissal"),
        ("horologion.dismissal_small", "Small dismissal"),
        ("horologion.dismissal_small_prayers", "Dismissal prayers"),
        ("horologion.dismissal_small_with_litany", "Dismissal with litany"),
        ("horologion.doxology_great", "Glory to Thee who hast shown us the light..."),
        ("horologion.doxology_small_read", "Glory to God in the highest..."),
        ("horologion.glory_to_holy", "Glory to the holy, consubstantial..."),
        ("horologion.have_mercy_on_us_lord", "Have mercy on us, O Lord..."),
        ("horologion.heavenly_choir", "The heavenly choir praises Thee..."),
        ("horologion.hexapsalmos", "The Six Psalms introduction"),
        ("horologion.invitatory_3x", "Come let us worship... (3x)"),
        ("horologion.it_is_a_good_thing", "It is a good thing to give thanks..."),
        ("horologion.kathisma_9", "Kathisma 9"),
        ("horologion.kontakion_have_mercy_on_us", "Have mercy on us, O Lord..."),
        ("horologion.litany_fervent", "Have mercy on us, O God..."),
        ("horologion.litany_final_compline", "Final compline litany"),
        ("horologion.litany_supplication", "Let us complete our prayer..."),
        ("horologion.lord_have_mercy_12", "Lord, have mercy. (12x)"),
        ("horologion.lord_have_mercy_3x", "Lord, have mercy. (3x)"),
        ("horologion.lord_have_mercy_40", "Lord, have mercy. (40x)"),
        ("horologion.nunc_dimittis", "Now lettest Thou Thy servant depart..."),
        ("horologion.o_gladsome_light_read", "O gladsome light..."),
        ("horologion.only_begotten", "Only-begotten Son and Word of God..."),
        ("horologion.our_father", "Our Father, who art in heaven..."),
        ("horologion.praises_psalms", "Let everything that hath breath..."),
        ("horologion.prayer_absolution_dead", "Prayer of absolution for the deceased"),
        ("horologion.prayer_compline_grant_us", "Grant us, O Lord..."),
        ("horologion.prayer_compline_spotless", "O Lord...keep us this night..."),
        ("horologion.prayer_hour_1_christ_true_light", "O Christ, the true Light..."),
        ("horologion.prayer_hour_3_mardari", "O Lord...who at the third hour..."),
        ("horologion.prayer_hour_6_god_and_lord_of_hosts", "O God and Lord of hosts..."),
        ("horologion.prayer_hour_9_master_lord", "O Master, Lord Jesus Christ..."),
        ("horologion.prayer_hours_thou_who", "O Thou who at all times and every hour..."),
        ("horologion.prayer_manasses", "Prayer of Manasses"),
        ("horologion.prayer_remember_fathers_brethren", "Remember, O Lord, our fathers..."),
        ("horologion.protection_christians", "O protection of Christians..."),
        ("horologion.psalm_102_bless_the_lord", "Bless the Lord, O my soul..."),
        ("horologion.psalm_118_blameless", "Blessed are the blameless..."),
        ("horologion.psalm_145_praise_the_lord", "Praise the Lord, O my soul..."),
        ("horologion.psalm_19", "May the Lord hear thee..."),
        ("horologion.psalm_20", "O Lord, in Thy strength..."),
        ("horologion.remember_us_o_lord", "Remember us, O Lord..."),
        ("horologion.remit_pardon", "Remit, pardon, forgive, O God..."),
        ("horologion.six_psalms", "The Six Psalms content"),
        ("horologion.supplication_all_holy_lady", "All-holy Lady Theotokos..."),
        ("horologion.trisagion_block", "Holy God, Holy Mighty..."),
        ("horologion.trop_repose_mother_holy", "O Mother most holy..."),
        ("horologion.trop_repose_remember_o_lord", "Remember, O Lord, the soul..."),
        ("horologion.troparia_compline_day_passed", "The day is past..."),
        ("horologion.troparion_illumine_my_eyes", "Illumine mine eyes, O Christ..."),
        ("horologion.verses_hour_1_order_my_steps", "Order my steps..."),
        ("horologion.verses_hour_3_blessed_is_the_lord", "Blessed is the Lord..."),
        ("horologion.verses_hour_6_compassions_quickly", "Let Thy compassions quickly..."),
        ("horologion.verses_hour_9_forsake_not", "Forsake us not utterly..."),
        ("horologion.vigil_bridge_blessing", "Vigil bridge blessing"),
        ("horologion.vouchsafe_o_lord", "Vouchsafe, O Lord..."),
    ],
    "text_triodion.json": [
        ("triodion.alleluia_passion", "Alleluia for Passion Week"),
        ("triodion.beatitudes_lenten", "Lenten Beatitudes"),
        ("triodion.canon_great_friday", "Good Friday Canon"),
        ("triodion.canon_tomb_complete", "Holy Saturday Tomb Canon"),
        ("triodion.communion_hymn_taste_and_see", "O taste and see..."),
        ("triodion.dismissal_presanctified", "Presanctified Dismissal"),
        ("triodion.hour_1_lenten_troparia_verses", "Lenten Hour 1 Troparia"),
        ("triodion.hour_3_lenten_troparia_verses", "Lenten Hour 3 Troparia"),
        ("triodion.hour_6_lenten_troparia_verses", "Lenten Hour 6 Troparia"),
        ("triodion.hour_9_lenten_troparia_verses", "Lenten Hour 9 Troparia"),
        ("triodion.lenten_kontakia_hours", "Lenten Kontakia for Hours"),
        ("triodion.let_my_prayer_arise", "Let my prayer arise..."),
        ("triodion.now_the_powers_of_heaven", "Now the powers of heaven..."),
        ("triodion.praises_great_friday", "Good Friday Praises"),
        ("triodion.prayer_st_ephrem", "O Lord and Master of my life..."),
        ("triodion.remember_us_solemn", "Solemn Remember us, O Lord..."),
        ("triodion.standing_in_the_temple", "Standing in the temple..."),
        ("triodion.troparion_glorious_disciples", "O glorious disciples..."),
        ("triodion.troparion_when_thou_didst_descend", "When Thou didst descend..."),
    ],
    "text_pentecostarion.json": [
        ("pentecostarion.canon_pascha", "Paschal Canon"),
        ("pentecostarion.christ_is_risen_3x", "Christ is risen! (3x)"),
        ("pentecostarion.dismissal_paschal_full", "May He who rose from the dead..."),
        ("pentecostarion.dismissal_paschal_hours", "Paschal Hours Dismissal"),
        ("pentecostarion.having_beheld_resurrection_3x", "Having beheld the resurrection... (3x)"),
        ("pentecostarion.hypakoe_pascha", "Paschal Hypakoe"),
        ("pentecostarion.kontakion_pascha", "Though Thou didst descend into the grave..."),
        ("pentecostarion.opening_let_god_arise", "Let God arise..."),
        ("pentecostarion.troparia_paschal_hours", "Paschal Hours Troparia"),
    ],
}

def add_missing_keys():
    """Add stub entries for missing keys."""
    total = 0
    
    for filename, keys in MISSING_KEYS.items():
        filepath = os.path.join(STAMFORD_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        added = 0
        for key, desc in keys:
            if key not in data:
                data[key] = {
                    "content": {"en": f"[STUB] {desc}"},
                    "_stub": True,
                    "_description": desc
                }
                added += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"  {filename}: {added} stub keys added")
        total += added
    
    return total

def main():
    print("=" * 60)
    print("ADDING MISSING KEY STUBS")
    print("=" * 60)
    
    total = add_missing_keys()
    
    print(f"\nComplete: {total} stub keys added")
    print("\nThese stubs need content from source texts.")

if __name__ == "__main__":
    main()
