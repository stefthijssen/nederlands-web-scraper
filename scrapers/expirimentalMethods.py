from langdetect import detect, detect_langs
import pycountry

countryCodes = list(map(lambda x: x.alpha_2.lower(), list(pycountry.countries)))

def verifyOrigin(url):
    # TODO:
    return False

def isDutch(str):
    code = detect(str)
    getPercentageDutch(str)
    print(str)
    print(code)
    return 'nl' == code

def getPercentageDutch(str):
    # TODO:
    return 0.5

def getDomainName(url):
    parts = url.split("/")[2].replace("www.", "").replace("ww2.", "").replace("ww3.", "").replace("ww4.", "").replace("ww5.", "").split(".")
    domainName = " ".join(parts[:len(parts)-1])
    return domainName

def getTopLevelDomain(url):
    parts = url.split("/")[2].split(".")
    return parts[len(parts)-1]

def getSubDirectories(url):
    parts = url.split("/")
    return " ".join(parts[3:len(parts)])

def fA(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    if (topLevelDomain == 'nl' or topLevelDomain == 'sr'):
        return True
    if (topLevelDomain in countryCodes):
        return False
    return False

def fB(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    domainName = getDomainName(url)
    if (topLevelDomain == 'nl'):
        return True
    if (topLevelDomain == 'be' or topLevelDomain == 'sr'):
        return isDutch(domainName)
    if (topLevelDomain in countryCodes):
        return False
    return isDutch(domainName)

def fC(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    domainName = getDomainName(url)
    subDirectories = getSubDirectories(url)
    if (topLevelDomain == 'nl'):
        return True
    if (topLevelDomain == 'be' or topLevelDomain == 'sr'):
        return isDutch(domainName + " " + subDirectories)
    if (topLevelDomain in countryCodes):
        return False
    return isDutch(domainName + " " + subDirectories)

def fD(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    domainName = getDomainName(url)
    subDirectories = getSubDirectories(url)
    if (topLevelDomain == 'nl'):
        return True
    if (topLevelDomain == 'be' or topLevelDomain == 'sr'):
        if isDutch(domainName + " " + subDirectories):
            return True
        else:
            return verifyOrigin(url)
    if (topLevelDomain in countryCodes):
        return False
    if isDutch(domainName + " " + subDirectories):
        return True
    else:
        return verifyOrigin(url)

def fE(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    domainName = getDomainName(url)
    subDirectories = getSubDirectories(url)
    if (topLevelDomain == 'nl'):
        return True
    if (topLevelDomain == 'be' or topLevelDomain == 'sr'):
        if isDutch(domainName + " " + subDirectories):
            return True
        else:
            return verifyOrigin(url)
    if (topLevelDomain in countryCodes):
        return False
    if isDutch(domainName + " " + subDirectories):
        return True
    else:
        return verifyOrigin(url)