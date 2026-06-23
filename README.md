# Sikh Empire: Ranjit Singh for Civilization VI

A custom Civilization VI mod that adds the Sikh Empire led by Maharaja Ranjit Singh as a high-power military, faith, and food civilization for `Rise & Fall` and `Gathering Storm`.

## Current Working Version

`v27` is the verified working build. Leader art, civilization icons, unit icons, building icons, ability icons, and setup-screen assets are loading correctly in Civilization VI after the DDS atlas encoding fix.

## Features

- New civilization: `Sikh Empire`
- New leader: `Maharaja Ranjit Singh`
- Civilization ability: `Chardi Kala`
- Leader ability: `Miri-Piri`
- Unique unit: `Akali Nihang` replacing the `Man-at-Arms`
- Unique unit: `Misldar Cavalry` replacing the `Cuirassier`
- Unique building: `Gurdwara Sahib` replacing the `Temple`
- Custom city list rooted in the Sikh Empire
- Custom named rivers for the Panjab region
- Custom leader, civ, unit, building, and ability art assets

## Civilization Overview

### Maharaja Ranjit Singh

`Miri-Piri`

- All land combat units ignore combat penalties from being wounded
- Defeating enemy units grants Faith equal to 50% of the defeated unit's Combat Strength
- Cities receive +15% Production toward military units

### Sikh Empire

`Chardi Kala`

- Cities founded on or adjacent to a river receive +2 Food and +1 Faith in the City Center
- Farms adjacent to a river receive +1 Faith
- Farms adjacent to both a river and a Holy Site receive +1 Production
- After researching `Irrigation`, river-adjacent Farms receive an additional +1 Food
- After researching `Civil Engineering`, river-adjacent Farms receive +1 Production
- Floodplains provide +1 Faith
- All combat units receive +5 Combat Strength against units of a civilization following a rival majority religion

## Unique Content

### Akali Nihang

A stronger, faster medieval melee replacement for the `Man-at-Arms` that can be purchased with Faith, ignores combat penalties from being wounded, and gains +5 Combat Strength.

### Misldar Cavalry

A stronger, faster industrial heavy cavalry replacement for the `Cuirassier` that can be purchased with Faith, ignores combat penalties from being wounded, gains +4 Combat Strength, and pillages for only 1 Movement.

### Gurdwara Sahib

A unique `Temple` replacement that provides:

- +4 Faith
- +2 Food
- +1 Housing
- +1 Great Prophet point per turn
- +1 Great General point per turn

## Supported Rulesets

- `Rise & Fall`
- `Gathering Storm`

The mod is built for the full expansion rulesets and is intended to be playable with both major DLCs enabled.

## Installation

Copy the mod folder into your Civilization VI mods directory:

`~/Library/Application Support/Sid Meier's Civilization VI/Sid Meier's Civilization VI/Mods/`

Then enable the mod from the in-game `Additional Content` menu.

## Repository Layout

- `Gameplay/` gameplay definitions and balance
- `Text/` localization, loading screen, and civilopedia text
- `Icons/` icon atlas mappings
- `Configuration/` frontend and setup integration
- `Art/` leader art, civ icon art, and DDS assets
- `Docs/` design notes

## Notes

- The mod uses Civilization VI's native rival-majority-religion combat hook for the religious combat bonus.
- Civilization VI does not expose a stable fractional flood-damage reduction modifier for districts and improvements, so full flood immunity is not used.
