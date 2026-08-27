from .base import DigestGeneratorBase
from .formatters.vespers import VespersFormatterMixin
from .formatters.matins import MatinsFormatterMixin
from .formatters.liturgy import LiturgyFormatterMixin
from .formatters.hours import HoursFormatterMixin
from .formatters.compline import ComplineFormatterMixin
from .formatters.lenten import LentenFormatterMixin
from .formatters.paschal import PaschalFormatterMixin
from .formatters.ceremonial import CeremonialFormatterMixin
from .formatters.common import CommonFormatterMixin
from .formatters.footnotes import FootnoteFormatterMixin

class TypikonDigestGenerator(
    DigestGeneratorBase,
    VespersFormatterMixin,
    MatinsFormatterMixin,
    LiturgyFormatterMixin,
    HoursFormatterMixin,
    ComplineFormatterMixin,
    LentenFormatterMixin,
    PaschalFormatterMixin,
    CeremonialFormatterMixin,
    CommonFormatterMixin,
    FootnoteFormatterMixin,
):
    pass