import json
import os

db_path = "json_db/stamford/text_octoechos.json"

troparia = {
    "tone_1.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 1)",
        "content" : "Though the stone was sealed by the Judeans, and soldiers guarded Your most pure body, You arose, O Savior, on the third day, and gave life to the world. Therefore, the heavenly powers cried out to You, the Giver of Life: Glory to Your Resurrection, O Christ! Glory to Your Kingdom! Glory to Your saving plan, O only Lover of mankind."
    },
    "tone_2.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 2)",
        "content" : "When You went down to death, O Life Immortal, You struck Hades dead with the blazing light of Your divinity. When You raised the dead from the nether world, all the powers of heaven cried out: O Giver of Life, Christ our God, glory be to You!"
    },
    "tone_3.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 3)",
        "content" : "Let the heavens be glad, let the earth rejoice, for the Lord has done a mighty deed with His arm. He trampled death by death. He became the first-born of the dead; He saved us from the abyss of Hades and granted great mercy to the world."
    },
    "tone_4.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 4)",
        "content" : "When the disciples of the Lord learned from the angel the glorious news of the resurrection and cast off the ancestral condemnation, they proudly told the apostles: Death has been plundered! Christ our God is risen, granting to the world great mercy."
    },
    "tone_5.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 5)",
        "content" : "Let us the faithful praise and worship the Word, co-eternal with the Father and the Spirit, born for our salvation from the Virgin; for He willed to be lifted up on the cross in the flesh, to endure death, and to raise the dead by His glorious resurrection."
    },
    "tone_6.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 6)",
        "content" : "Angelic powers were upon Your tomb and the guards became like dead men; Mary stood before the tomb seeking Your most pure body. You captured Hades without being overcome by it. You met the Virgin and granted life. O Lord, risen from the dead, glory be to You!"
    },
    "tone_7.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 7)",
        "content" : "by Your cross You destroyed death; You opened Paradise to the thief; You changed the lamentation of the myrrh-bearers to joy, and charged the apostles to proclaim that You are risen, O Christ our God, offering great mercy to the world."
    },
    "tone_8.troparion.resurrection": {
        "title": "Resurrection Troparion (Tone 8)",
        "content" : "You came down from on high, O Merciful One, and accepted three days of burial to free us from our sufferings. O Lord, our life and our resurrection, glory to You!"
    }
}

def run():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Inject
    for k, v in troparia.items():
        data[k] = v
        print(f"Injected {k}")
        
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("Text Octoechos updated.")

if __name__ == "__main__":
    run()
