$( function() {
    var availableTags = [
        {% for ticker in homepage_data.all_ticker %}
            "{{ticker}}",
        {% endfor %}
    ];
    $( "#ticker-search" ).autocomplete({
      source: availableTags
    });
  } );
