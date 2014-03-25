'''
SunThemeSwitcher Theme and Scheme Changer
'''
import datetime
from math import degrees, radians, atan2, cos, sin, pi, sqrt, fabs

import sublime


class SunriseSunset(object):

    """
    This class determines the sunrise and sunset for zenith standards for the
    given day. It can also tell you if the given time is during the nigh or
    day.
    """
    __ZENITH = {'official': -0.833,
                'civil': -6.0,
                'nautical': -12.0,
                'amateur': -15.0,
                'astronomical': -18.0}

    def __init__(self, date, lat, lon, zenith='official'):
        """
        Set the values for the sunrise and sunset calculation.

        @param date: A localized datetime object that is timezone aware.
        @param lat: The latitude.
        @param lon: The longitude.
        @keyword zenith: The zenith name.
        """
        if not isinstance(date, datetime.datetime) or date.tzinfo is None:
            msg = "The date must be a datetime object with timezone info."
            raise ValueError(msg)

        if zenith not in self.__ZENITH:
            msg = "Invalid zenith name [%s] must be one of: %s"
            raise ValueError(msg % (zenith, self.__ZENITH.keys()))

        if abs(lat) > 63:
            raise ValueError('Invalid latitude: %s' % lat)

        self.__dateLocal = date
        self.__lat = lat
        self.__lon = lon
        self.__zenith = zenith
        localTuple = date.timetuple()
        utcTuple = date.utctimetuple()
        self.__offsetUTC = (localTuple[3] - utcTuple[3]) + \
                           (localTuple[4] - utcTuple[4]) / 60.0
        self.__sunrise = None
        self.__sunset = None
        self.__determineRiseSet()

    def isNight(self, collar=0):
        """
        Check if it is day or night. If the 'collar' keyword argument is
        changed it will skew the results to either before or after the real
        sunrise and sunset. This is useful if lead and lag timea are needed
        around the actual sunrise and sunset.

        Note::
            If collar == 30 then this method will say it is daytime 30
            minutes before the actual sunrise and likewise 30 minutes after
            sunset it would indicate it is night.

        @keyword collar: The minutes before or after sunrise and sunset.
        @return: True if it is night else False if day.
        """
        result = False
        delta = datetime.timedelta(minutes=collar)

        if (self.__sunrise - delta) > self.__dateLocal or \
                self.__dateLocal > (self.__sunset + delta):
            result = True

        return result

    def getSunRiseSet(self):
        """
        Get the sunrise and sunset.

        @return: A C{datetime} object in a tuple (sunrise, sunset).
        """
        return self.__sunrise, self.__sunset

    def __determineRiseSet(self):
        """
        Determine both the sunrise and sunset.
        """
        year = self.__dateLocal.year
        month = self.__dateLocal.month
        day = self.__dateLocal.day
        # Ephemeris
        ephem2000Day = 367 * year - (7 * (year + (month + 9) / 12) / 4) + \
            (275 * month / 9) + day - 730531.5
        self.__sunrise = self.__determineRiseOrSet(ephem2000Day, 1)
        self.__sunset = self.__determineRiseOrSet(ephem2000Day, -1)

    def __determineRiseOrSet(self, ephem2000Day, rs):
        """
        Determine either the sunrise or the sunset.

        @param ephem2000Day: The Ephemeris from the beginning of the
                             21st century.
        @param rs: The factor that determines either sunrise or sunset where
                   1 equals sunrise and -1 sunset.
        @return: Either the sunrise or sunset as a C{datetime} object.
        """
        utold = pi
        utnew = 0
        altitude = self.__ZENITH[self.__zenith]
        sinAlt = sin(radians(altitude))       # solar altitude
        sinPhi = sin(radians(self.__lat))     # viewer's latitude
        cosPhi = cos(radians(self.__lat))     #
        lon = radians(self.__lon)             # viewer's longitude
        ct = 0
        # print rs, ephem2000Day, sinAlt, sinPhi, cosPhi, lon

        while fabs(utold - utnew) > 0.001 and ct < 35:
            ct += 1
            utold = utnew
            days = ephem2000Day + utold / (2 * pi)
            t = days / 36525
            # The magic numbers are orbital elements of the sun.
            l = self.__getRange(4.8949504201433 + 628.331969753199 * t)
            g = self.__getRange(6.2400408 + 628.3019501 * t)
            ec = 0.033423 * sin(g) + 0.00034907 * sin(2 * g)
            lam = l + ec
            e = -1 * ec + 0.0430398 * sin(2 * lam) - 0.00092502 * sin(4 * lam)
            obl = 0.409093 - 0.0002269 * t
            delta = sin(obl) * sin(lam)
            delta = atan2(delta, sqrt(1 - delta * delta))
            gha = utold - pi + e
            cosc = (sinAlt - sinPhi * sin(delta)) / (cosPhi * cos(delta))

            if cosc > 1:
                correction = 0
            elif cosc < -1:
                correction = pi
            else:
                correction = atan2((sqrt(1 - cosc * cosc)), cosc)

            # print cosc, correction, utold, utnew
            utnew = self.__getRange(utold - (gha + lon + rs * correction))

        decimalTime = degrees(utnew) / 15
        # print utnew, decimalTime
        return self.__get24HourLocalTime(rs, decimalTime)

    def __getRange(self, value):
        """
        Get the range of the value.

        @param value: The domain.
        @return: The resultant range.
        """
        tmp1 = value / (2.0 * pi)
        tmp2 = (2.0 * pi) * (tmp1 - int(tmp1))
        if tmp2 < 0.0:
            tmp2 += (2.0 * pi)
        return tmp2

    def __get24HourLocalTime(self, rs, decimalTime):
        """
        Convert the decimal time into a local time (C{datetime} object)
        and correct for a 24 hour clock.

        @param rs: The factor that determines either sunrise or sunset where
                   1 equals sunrise and -1 sunset.
        @param decimalTime: The decimal time.
        @return: The C{datetime} objects set to either sunrise or sunset.
        """
        decimalTime += self.__offsetUTC
        # print decimalTime

        if decimalTime < 0.0:
            decimalTime += 24.0
        elif decimalTime > 24.0:
            decimalTime -= 24.0

        # print decimalTime
        hour = int(decimalTime)
        tmp = (decimalTime - hour) * 60
        minute = int(tmp)
        tmp = (tmp - minute) * 60
        second = int(tmp)
        micro = int(round((tmp - second) * 1000000))
        localDT = self.__dateLocal.replace(hour=hour, minute=minute,
                                           second=second, microsecond=micro)
        return localDT


class make_tz(datetime.tzinfo):

    def __init__(self, offset):
        self.offset = offset
        self.utc_offset = datetime.timedelta(hours=offset)

    def utcoffset(self, dt):
        return self.utc_offset

    def tzname(self, dt):
        return "UTC Offset %0.1f" % self.offset

    def dst(self, dt):
        return datetime.timedelta(0)

    def __str__(self):
        return "UTC Offset %0.1f" % self.offset


class SunThemeSwitcher():

    def __init__(self):
        settings = sublime.load_settings('SunThemeSwitcher.sublime-settings')
        self.checkDelay = int(settings.get('checkCycle', 2) * 1000)
        timezone = settings.get('timezone')
        try:
            self.tz_info = make_tz(float(timezone))
        except ValueError:
            # If ValueError is raised, then string must of been entered
            import pytz
            self.tz_info = pytz.timezone(timezone)
        # Check if over riding the time is on, else set from calculation.
        if settings.get('overrideTimes', False):
            self.sunrise_time = datetime.datetime.strptime(
                settings.get('overrideSunriseTime'), '%H:%M')
            self.sunset_time = datetime.datetime.strptime(
                settings.get('overrideSunsetTime'), '%H:%M')
        else:
            datetime_now = datetime.datetime.now(self.tz_info)
            s = SunriseSunset(
                datetime_now, settings.get('latitude'),
                settings.get('longitude'))
            self.sunrise_time, self.sunset_time = s.getSunRiseSet()

    def changeScheme(self, desiredScheme='', desiredTheme=''):
        sublimeSettings = sublime.load_settings('Preferences.sublime-settings')
        if desiredScheme:
            currentScheme = sublimeSettings.get('color_scheme')
            if currentScheme != desiredScheme:
                print "Switching to new colour scheme: %s" % desiredScheme
                sublimeSettings.set('color_scheme', desiredScheme)
        if desiredTheme:
            currentTheme = sublimeSettings.get('theme')
            if currentTheme != desiredTheme:
                print "Switching to new window theme: %s" % desiredTheme
                sublimeSettings.set('theme', desiredTheme)

    def isItDark(self):
        datetime_now = datetime.datetime.now()
        settings = sublime.load_settings('SunThemeSwitcher.sublime-settings')
        # Check for forces
        if settings.get('forceNight'):
            return True
        if settings.get('forceDay'):
            return False
        # This is ugly, but timezone aware comparing can be difficult with
        # non timezone aware times.
        if self.sunrise_time.hour < datetime_now.hour < self.sunset_time.hour:
            return False
        elif self.sunrise_time.hour == datetime_now.hour:
            if self.sunrise_time.minute < datetime_now.minute:
                return False
            else:
                return True
        elif datetime_now.hour == self.sunset_time.hour:
            if datetime_now.minute < self.sunset_time.minute:
                return False
            else:
                return True
        else:
            return True

    def setCorrectScheme(self):
        settings = sublime.load_settings('SunThemeSwitcher.sublime-settings')
        if self.isItDark():
            correctScheme = settings.get('nightColourScheme', '')
            correctTheme = settings.get('nightWindowTheme', '')
        else:
            correctScheme = settings.get('dayColourScheme', '')
            correctTheme = settings.get('dayWindowTheme', '')
        self.changeScheme(correctScheme, correctTheme)

    def run(self):
        sublime.set_timeout(self.run, self.checkDelay)
        self.setCorrectScheme()


if 'runSunThemeSwitcher' not in globals():
    try:
        switcher = SunThemeSwitcher()
        switcher.run()
        runSunThemeSwitcher = True
        print "SunThemeSwitcher using Timezone: %s" % str(switcher.tz_info)
        print "SunThemeSwitcher using Sunrise time: %s" % \
            switcher.sunrise_time.strftime('%H:%M')
        print "SunThemeSwitcher using Sunset  time: %s" % \
            switcher.sunset_time.strftime('%H:%M')
    except ImportError:
        print "You need to install pytz, or use a basic gmt offset value for timezone."
    except AttributeError:
        print "SunThemeSwitcher is improperly configured, please see README"
