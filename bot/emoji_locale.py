KNOWN_CODES = {
    'af': 'ZA',
    'agq': 'CM',
    'ak': 'GH',
    'am': 'ET',
    'ar': 'AE',
    'as': 'IN',
    'asa': 'TZ',
    'az': 'AZ',
    'bas': 'CM',
    'be': 'BY',
    'bem': 'ZM',
    'bez': 'IT',
    'bg': 'BG',
    'bm': 'ML',
    'bn': 'BD',
    'bo': 'CN',
    'br': 'FR',
    'brx': 'IN',
    'bs': 'BA',
    'ca': 'ES',
    'cgg': 'UG',
    'chr': 'US',
    'cs': 'CZ',
    'cy': 'GB',
    'da': 'DK',
    'dav': 'KE',
    'de': 'DE',
    'dje': 'NE',
    'dua': 'CM',
    'dyo': 'SN',
    'ebu': 'KE',
    'ee': 'GH',
    'en': 'GB',
    'el': 'GR',
    'es': 'ES',
    'et': 'EE',
    'eu': 'ES',
    'ewo': 'CM',
    'fa': 'IR',
    'fil': 'PH',
    'fr': 'FR',
    'ga': 'IE',
    'gl': 'ES',
    'gsw': 'CH',
    'gu': 'IN',
    'guz': 'KE',
    'gv': 'GB',
    'ha': 'NG',
    'haw': 'US',
    'he': 'IL',
    'hi': 'IN',
    'ff': 'CN',
    'fi': 'FI',
    'fo': 'FO',
    'hr': 'HR',
    'hu': 'HU',
    'hy': 'AM',
    'id': 'ID',
    'ig': 'NG',
    'ii': 'CN',
    'is': 'IS',
    'it': 'IT',
    'ja': 'JP',
    'jmc': 'TZ',
    'ka': 'GE',
    'kab': 'DZ',
    'ki': 'KE',
    'kam': 'KE',
    'mer': 'KE',
    'kde': 'TZ',
    'kea': 'CV',
    'khq': 'ML',
    'kk': 'KZ',
    'kl': 'GL',
    'kln': 'KE',
    'km': 'KH',
    'kn': 'IN',
    'ko': 'KR',
    'kok': 'IN',
    'ksb': 'TZ',
    'ksf': 'CM',
    'kw': 'GB',
    'lag': 'TZ',
    'lg': 'UG',
    'ln': 'CG',
    'lt': 'LT',
    'lu': 'CD',
    'lv': 'LV',
    'luo': 'KE',
    'luy': 'KE',
    'mas': 'TZ',
    'mfe': 'MU',
    'mg': 'MG',
    'mgh': 'MZ',
    'ml': 'IN',
    'mk': 'MK',
    'mr': 'IN',
    'ms': 'MY',
    'mt': 'MT',
    'mua': 'CM',
    'my': 'MM',
    'naq': 'NA',
    'nb': 'NO',
    'nd': 'ZW',
    'ne': 'NP',
    'nl': 'NL',
    'nmg': 'CM',
    'nn': 'NO',
    'nus': 'SD',
    'nyn': 'UG',
    'om': 'ET',
    'or': 'IN',
    'pa': 'PK',
    'pl': 'PL',
    'ps': 'AF',
    'pt': 'PT',
    'rm': 'CH',
    'rn': 'BI',
    'ro': 'RO',
    'ru': 'RU',
    'rw': 'RW',
    'rof': 'TZ',
    'rwk': 'TZ',
    'saq': 'KE',
    'sbp': 'TZ',
    'seh': 'MZ',
    'ses': 'ML',
    'sg': 'CF',
    'shi': 'MA',
    'si': 'LK',
    'sk': 'SK',
    'sl': 'SI',
    'sn': 'ZW',
    'so': 'SO',
    'sq': 'AL',
    'sr': 'RS',
    'sv': 'SE',
    'sw': 'TZ',
    'swc': 'CD',
    'ta': 'IN',
    'te': 'IN',
    'teo': 'UG',
    'th': 'TH',
    'ti': 'ET',
    'to': 'TO',
    'tr': 'TR',
    'twq': 'NE',
    'tzm': 'MA',
    'uk': 'UA',
    'ur': 'PK',
    'uz': 'UZ',
    'vai': 'LR',
    'vi': 'VN',
    'vun': 'TZ',
    'xog': 'UG',
    'yav': 'CM',
    'yo': 'NG',
    'zh': 'CN',
    'zh-cn': 'CN',
    'zh-tw': 'TW',
    'zu': 'ZA'
}

# Returns a country's flag according to ISO 639-1 language code
# Note: Some languages could return just two regional indicator letter emojis (if that combination doesn't create a flag emoji)
#       Doesn't cover every ISO 639-1 code
# Returns empty string for invalid/unknown ISO 639-1 language codes
def code_to_country(code):
    if not code:
        return ''
    elif code in KNOWN_CODES:
        country = KNOWN_CODES.get(code)
        # Unicode: chr(ord('A') + 127397) = 🇦
        # 🇬 + 🇧 = 🇬🇧
        return chr(ord(country[0]) + 127397) + chr(ord(country[1]) + 127397)
    return ''
