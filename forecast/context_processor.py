from .models import TickerList
from .forms import SearchForm

def get_tickerlist(request):

    return {'all_ticker': TickerList.objects.all().values_list('ticker', flat=True)}