import json
import os

fundamentals = {
    # Semiconductors
    "HCL Tech": 85, "Tata Elxsi": 82, "Dixon Technologies": 78, "CG Power": 75,
    "Kaynes Technology": 72, "Vedanta": 65, "BEL": 88, "Data Patterns": 71,
    "Syrma SGS": 60, "Cyient DLM": 62, "PG Electroplast": 68, "Avalon Technologies": 55,
    "MosChip Tech": 45, "Paras Defence": 42,
    
    # Ancillary
    "ASM Tech (Equip)": 40, "RIR Power (SiC)": 55, "SPEL Semi (OSAT)": 35,
    "Linde India (Gases)": 80, "Navin Fluorine (Chems)": 77, "Archean Chem (Chems)": 65,
    "Stallion India (Chems)": 50, "Amber Ent (PCB)": 70, "Hitachi Energy (Power)": 85,
    "L&T Tech (Design)": 82, "Tata Chemicals (Silica)": 75,
    
    # Nuclear
    "BHEL (Main)": 60, "L&T (Main)": 90, "Walchandnagar (Main)": 40, "Godrej Ind (Main)": 75,
    "Thermax (Ancillary)": 82, "KSB Ltd (Ancillary)": 78, "GMM Pfaudler (Ancillary)": 65,
    "Apar Ind (Ancillary)": 85, "Graphite India (Ancillary)": 55, "MTAR Tech (Ancillary)": 70,
    
    # Water
    "VA Tech Wabag (Main)": 68, "Ion Exchange (Main)": 75, "EMS Ltd (Main)": 65,
    "Enviro Infra (Main)": 60, "Supreme Ind (Ancillary)": 85, "Astral (Ancillary)": 88,
    "Prince Pipes (Ancillary)": 72, "Finolex Ind (Ancillary)": 70, "Kirloskar Bros (Ancillary)": 68,
    "Shakti Pumps (Ancillary)": 66,
    
    # Drones
    "ideaForge (Main)": 45, "Zen Tech (Main)": 64, "Paras Defence (Main)": 42,
    "Data Patterns (Main)": 71, "BEL (Ancillary)": 88, "Astra Microwave (Ancillary)": 60,
    "Solar Ind (Ancillary)": 85, "HAL (Ancillary)": 92, "Laurus Labs (Ancillary)": 70,
    "Cyient (Ancillary)": 75,
    
    # Data Center
    "Anant Raj (Main)": 66, "Netweb Tech (Main)": 75, "RateGain (Main)": 70,
    "Blue Star (Ancillary)": 78, "Voltas (Ancillary)": 56, "ABB India (Ancillary)": 88,
    "Siemens India (Ancillary)": 85, "Polycab (Ancillary)": 82, "Sterlite Tech (Ancillary)": 45,
    "HFCL (Ancillary)": 55, "Schneider India (Ancillary)": 80,
    
    # Hydrogen
    "L&T (Main)": 90, "NTPC (Main)": 85, "Indian Oil (Main)": 75, "GAIL (Main)": 78,
    "Thermax (Ancillary)": 82, "Praj Ind (Ancillary)": 75, "Kirloskar Oil (Ancillary)": 65,
    "Gujarat Fluoro (Ancillary)": 70, "Sterling & Wilson (Ancillary)": 55, "Deepak Fertilisers (Ancillary)": 60,
    
    # Rare Earths & Specialty Metals
    "NMDC (Main)": 82, "Hindustan Copper (Main)": 75, "GMDC (Main)": 68, "MOIL (Main)": 72, "Mishra Dhatu Nigam (Main)": 85,
    "Exide Industries (Ancillary)": 80, "Amara Raja (Ancillary)": 78, "Neogen Chemicals (Ancillary)": 85,
    "Himadri Speciality (Ancillary)": 88, "Tata Chemicals (Ancillary)": 82,
    
    # Green Energy & Infra
    "Tata Power (Main)": 88, "Adani Green (Main)": 75, "Suzlon Energy (Main)": 65, "JSW Energy (Main)": 82, "Waaree Renewables (Main)": 78,
    "Borosil Renewables (Ancillary)": 70, "Sterling and Wilson (Ancillary)": 65, "Genus Power (Ancillary)": 85,
    "Olectra Greentech (Ancillary)": 80, "Servotech Power (Ancillary)": 72,
    
    # IT Services & ER&D
    "TCS (Main)": 92, "Infosys (Main)": 90, "HCL Tech (Main)": 88, "LTIMindtree (Main)": 85, "Persistent Systems (Main)": 89,
    "KPIT Technologies (Ancillary)": 90, "Tata Elxsi (Ancillary)": 88, "RateGain (Ancillary)": 78,
    "Cyient (Ancillary)": 80, "MapmyIndia (Ancillary)": 75
}

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fundamentals.json')
with open(path, 'w') as f:
    json.dump(fundamentals, f, indent=4)
print("Fundamentals JSON generated successfully for 90 stocks.")
