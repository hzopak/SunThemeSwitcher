## SunThemeSwitcher

Changes a users Sublime Text 2 colour scheme automatically according to where
the sun is outside.

I wrote this as an alternative to NightCycle because I wanted a little bit more
automation depending on which season I'm in. However I included override
settings to give similar functionality as NightCycle if desired.

## Usage

Install in your preferred fashion, then restart Sublime Text.

Adjust the configuration:

Preferences menu -> Package Settings -> SunThemeSwitcher -> Settings - User

This file will initially be blank, look at the contents of "Settings - Default"
to get the configuration structure (it's easiest to copy the default
configuration over and then edit from that base).

## Basic rundown on the settings

**latitude**
A latitude number value between - 90 and 90 where positive numbers are North

**longitude**
    A longitude number value between - 180 and 180 where positive numbers are
    East

**timezone**
    Either a number specifing the GMT offset time value or a string of a valid
    pytz timezone.
    This is only used for sunrise / sunset calculations.
    To use pytz timezone's you need to install the pytz package.
    For a list of available timezones:
        open the python console and enter:
        >>> import pytz; pytz.all_timezones

**forceDay, forceNight**
    If either of these are set to true it will force that state. If both are set
    forceNight wins.
    Can be set at anytime for desired effect.

**overrideTimes**
    If this is set to true the script will not use sunrise / sunset times, but
    the times specified in
    overrideSunriseTime and overrideSunsetTime
    Requires sublime reload for this to happen.

**overrideSunriseTime, overrideSunsetTime**
    Time as a string in 24 hour time notation, use the default config as a guide
    if unsure.

**dayColourScheme, nightColourScheme**
    In Australia we put a 'u' in colour.
    String value indicating what scheme to use at what time.

**dayWindowTheme, nightWindowTheme**
    Same as above but for the window theme, not the colour scheme.
    I recommend: https://github.com/buymeasoda/soda-theme/

**checkCycle**
    A float in seconds of how often to check to see if it's night or day. This
    interval does not
    recalculate sunrise and sunset times. Default 5 seconds.
    Requires sublime reload for effect to take place.


## Acknowledgements

This has been mostly a copy of NightCycle
http://github.com/forty-two/NightCycle
With an implimentation of SunriseSunset class by Carl J. Nobile
http://wiki.tetrasys-design.net/SunriseSunset
