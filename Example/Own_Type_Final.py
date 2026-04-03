def classify_owner(propertyowner, taxdesc):
    """
    Classify property owners into categories: City, County, Utilities (PURTA), 
    Institution, Other Public, or Private.
    
    CLASSIFICATION RULES (in priority order):
    1. PURTA tax designation (12 - Public Utility Realty Tax) -> Utilities (PURTA)
    2. Churches and religious entities -> Institution (regardless of tax status)
    3. City of McKeesport entities -> City
    4. County entities -> County
    5. Tax-exempt (10 - Exempt) parcels -> Institution (if not already classified)
    6. Other public entities -> Other Public
    7. Everything else -> Private
    """
    # Normalize strings
    if propertyowner is None:
        o = ""
    else:
        o = str(propertyowner).upper()

    if taxdesc is None:
        t = ""
    else:
        t = str(taxdesc).upper()

    # RULE 1: PURTA (Public Utility Realty Tax) - highest priority
    if t.startswith("12 - PUBLIC UTILITY REALTY TAX"):
        return "Utilities (PURTA)"

    # RULE 2: Churches and religious institutions - ALWAYS Institution regardless of tax status
    church_keywords = [
        "CHURCH",
        "PARISH",
        "PRESBYTERIAN",
        "BAPTIST",
        "CATHOLIC",
        "LUTHERAN",
        "EPISCOPAL",
        "METHODIST",
        "TEMPLE",
        "SYNAGOGUE",
        "MOSQUE",
        "DIOCESE",
        "MINISTR",          # MINISTRY / MINISTRIES
        "MISSION",
        "CONGREGATION"
    ]
    for kw in church_keywords:
        if kw in o:
            return "Institution"

    # RULE 3: City of McKeesport entities
    if ("CITY OF MCKEESPORT" in o or
        "CITY OF MC KEESPORT" in o or
        ("MCKEESPORT" in o and "REDEVELOPMENT AUTHORITY" in o) or
        ("MCKEESPORT" in o and "PARKING AUTHORITY" in o) or
        ("MCKEESPORT" in o and "HOUSING AUTHORITY" in o)):
        return "City"

    # RULE 4: County entities
    if "ALLEGHENY COUNTY" in o or "COUNTY OF " in o:
        return "County"

    # RULE 5: Tax-exempt parcels are Institution (if not already classified above)
    # These are nonprofits, community organizations, social service providers, etc.
    if t == "10 - EXEMPT":
        return "Institution"

    # RULE 6: Exclude false positives before checking institution keywords
    # These contain institutional keywords but are actually private entities
    false_positive_patterns = [
        "HOSPITALITY CORP",           # Business, not hospital
        " LLC",                        # Limited Liability Companies
        " LP",                         # Limited Partnerships  
        " INC",                        # May be private corporations
        "INVESTMENT",
        "RENTAL"
    ]
    
    # Check if this looks like a personal name with "Charity" as first name
    # Pattern: "LASTNAME CHARITY FIRSTNAME" or "LASTNAME CHARITY"
    if " CHARITY " in o or o.endswith(" CHARITY"):
        # If it has typical personal name indicators, skip institution classification
        words = o.split()
        if len(words) <= 4 and not any(kw in o for kw in ["FOUNDATION", "TRUST", "ORGANIZATION"]):
            # Likely a personal name, will fall through to Private
            pass
        else:
            # Otherwise treat CHARITY as institutional keyword below
            pass
    
    # RULE 7: Federal agencies - check before other institution keywords
    # These should be Institution even if they have other keywords
    if "SECRETARY OF VETERANS" in o:
        return "Institution"
    
    if "SECRETARY OF" in o:
        return "Other Public"

    # RULE 8: Other charitable/nonprofit institutions (even if taxable)
    # Some institutions own taxable property (rental properties, businesses, etc.)
    # Check this AFTER false positive patterns
    has_false_positive = any(pattern in o for pattern in false_positive_patterns)
    
    other_institution_keywords = [
        "FOUNDATION",
        "CHARITABLE",
        "COMMUNITY SERVICES",
        "MON YOUGH COMMUNITY SERVICES",
        "MON-YOUGH COMMUNITY SERVICES",
        "HOSPITAL",
        "YOUNG MENS CHRISTIAN",
        "YMCA",
        "YWCA",
        "SALVATION ARMY",
        "LODGE",
        "VETERANS",
        "WELFARE ASSOCIATION",
        "NONPROFIT",
        "NON-PROFIT",
        "NON PROFIT"
    ]
    
    # Only apply institution keywords if no false positive patterns detected
    if not has_false_positive:
        for kw in other_institution_keywords:
            if kw in o:
                return "Institution"

    # RULE 9: Other Public entities (authorities, school districts, municipalities, federal/state)
    public_keywords = [
        "AUTHORITY",
        "SCHOOL DISTRICT",
        "BOROUGH OF",
        "TOWNSHIP OF",
        "COMMONWEALTH OF",
        "UNITED STATES",
        "US GOVT",
        "U S GOVERNMENT",
        "PENNSYLVANIA TURNPIKE",
        "PORT AUTHORITY"
    ]
    for kw in public_keywords:
        if kw in o:
            return "Other Public"

    # RULE 10: Private (fallback - all remaining parcels)
    # Includes private individuals, LLCs, corporations, partnerships, etc.
    return "Private"

__esri_field_calculator_splitter__
classify_owner(!PROPERTYOWNER!, !TAXDESC!)
