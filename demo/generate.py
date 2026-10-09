"""Generate varied, synthetic TXT examples for the first Sift integration slice."""

from __future__ import annotations

import json
from pathlib import Path


DESTINATION = Path(__file__).resolve().parent / "generated"

DOCUMENTS = [
    {
        "filename": "01c8.txt",
        "topic": "laptop repair receipt",
        "query": "receipt for my laptop repair",
        "text": "SERVICE INVOICE\nNorthline Computer Repair\nDevice: 14-inch laptop\nWork completed: replacement keyboard and trackpad cable\nTotal paid: PHP 2,500\nPayment: card\nWarranty: 90 days",
    },
    {
        "filename": "07af.txt",
        "topic": "photosynthesis class notes",
        "query": "class notes about how plants use light",
        "text": "BIOLOGY 101 — WEEK 4\nPhotosynthesis converts light energy into chemical energy. Chlorophyll absorbs light, and plants use water and carbon dioxide to produce glucose and oxygen.\nRemember: light-dependent reactions happen in the thylakoid membranes.",
    },
    {
        "filename": "12de.txt",
        "topic": "hotel booking confirmation",
        "query": "hotel booking in Cebu for the first week of August",
        "text": "TRAVEL CONFIRMATION\nHarborview Hotel Cebu\nStay: 3–6 August\nRoom: standard double\nReservation code: Q7M4P2\nBreakfast included. Check-in begins at 15:00.",
    },
    {
        "filename": "16b2.txt",
        "topic": "meeting notes about office plants",
        "query": "meeting notes about watering the office plants",
        "text": "WEDNESDAY TEAM NOTES\nFacilities will water the lobby plants every Tuesday. The fern near the north window needs less direct sun. Revisit the plant-care schedule next month.",
    },
    {
        "filename": "1d91.txt",
        "topic": "grocery list",
        "query": "shopping list with coffee and oranges",
        "text": "WEEKEND MARKET\nCoffee beans, oranges, rice, dish soap, and ginger. Ask the fruit seller which mangoes are ripe today.",
    },
    {
        "filename": "24e5.txt",
        "topic": "project notes about a campus map",
        "query": "notes about improving the campus map",
        "text": "MAP REFRESH\nAdd a step-free route between the library and science building. Check the new bicycle parking labels with facilities before printing the map.",
    },
    {
        "filename": "2aa0.txt",
        "topic": "family recipe",
        "query": "the recipe for coconut chicken stew",
        "text": "GINATAANG MANOK\nBrown chicken with garlic and onion. Add ginger, squash, and coconut milk. Simmer gently until the chicken is tender; finish with leafy greens and a little fish sauce.",
    },
    {
        "filename": "31f6.txt",
        "topic": "conference schedule",
        "query": "schedule for the design conference keynote",
        "text": "DESIGN FORUM\n09:00 registration\n10:15 keynote: Making public services easier to use\n13:30 accessible prototyping workshop\n16:00 closing remarks",
    },
    {
        "filename": "3bd8.txt",
        "topic": "running plan",
        "query": "my beginner running plan for the weekend",
        "text": "FOUR-WEEK PLAN\nSaturday: alternate one minute of easy running with two minutes of walking for twenty minutes. Sunday: rest, stretch, and prepare water for next week's sessions.",
    },
    {
        "filename": "44ac.txt",
        "topic": "library return reminder",
        "query": "when to return the borrowed history books",
        "text": "LIBRARY CARD\nReturn the two Southeast Asian history books by Friday. Renew online if the research project needs them for another week.",
    },
    {
        "filename": "50d1.txt",
        "topic": "electricity bill note",
        "query": "note about the monthly electricity payment",
        "text": "HOUSEHOLD REMINDER\nThe electric bill is due on the 18th. Compare this month's usage with the previous statement and save the confirmation number after payment.",
    },
    {
        "filename": "5c73.txt",
        "topic": "language study notes",
        "query": "Spanish vocabulary notes for ordering lunch",
        "text": "SPANISH PRACTICE\nQuisiera una mesa para dos, por favor.\nLa cuenta, por favor.\nToday: practise asking about vegetarian options and the lunch special.",
    },
    {
        "filename": "63e9.txt",
        "topic": "volunteer shift reminder",
        "query": "reminder for the Saturday community garden volunteer shift",
        "text": "COMMUNITY GARDEN\nSaturday shift starts at 08:30. Bring gloves and a refillable bottle. The seedling table is beside the rainwater tank.",
    },
    {
        "filename": "6f04.txt",
        "topic": "photo backup checklist",
        "query": "checklist for backing up family photos",
        "text": "PHOTO ARCHIVE\nCopy the family trip photos to the external drive, confirm the count matches the originals, and store the drive in the desk drawer. Do not delete the camera card until a second copy is checked.",
    },
    {
        "filename": "71aa.txt",
        "topic": "water delivery note",
        "query": "the building water delivery schedule",
        "text": "DELIVERY WINDOW\nWater refills arrive every other Thursday between 11:00 and 13:00. Keep the empty containers next to the service entrance.",
    },
    {
        "filename": "83cd.txt",
        "topic": "museum visit plan",
        "query": "plan for the museum visit and its photography rules",
        "text": "CITY MUSEUM\nMeet at the west entrance at 10:30. The textile gallery allows photography without flash; the archive room does not allow cameras.",
    },
]


def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in DOCUMENTS:
        (DESTINATION / item["filename"]).write_text(item["text"] + "\n", encoding="utf-8")
        manifest.append({key: item[key] for key in ("filename", "topic", "query")})
    (DESTINATION.parent / "manifest.json").write_text(
        json.dumps(
            {
                "synthetic": True,
                "note": "Generated examples; never use as evidence of retrieval quality or scale.",
                "targets": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(DOCUMENTS)} varied synthetic TXT files in {DESTINATION}")


if __name__ == "__main__":
    main()
