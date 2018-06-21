window.onload = function() {
  String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
  };

  var additionalNotes = window.additionalNotes.replaceAll("&lt;NEW_LINE&gt;", "\n");
  $("#notes").text(additionalNotes);

  var itemsStr = window.itemsStr.replaceAll("&quot;", '"');
  itemsStr = itemsStr.replaceAll("&lt;NEW_LINE&gt;", "\n");
  var items = JSON.parse(itemsStr);
  window.items = items;

  var partyDateStr = window.partyDateStr;
  var month = partyDateStr.substr(0,2);
  var day = partyDateStr.substr(3,2);
  var year = partyDateStr.substr(6,4);
  var partyDate = year + "-" + month + "-" + day;
  $("#party_date").val(partyDate);

  var pinataNameGuess = null;
  var pinataQtyGuess = null;

  for (i=0; i<items.length; i++) {
    var item = items[i];
    var item_imgs = [item.img];

    var displayStr = "<div>";
    displayStr += "<b>Quantity:</b> " + item.quantity + "<br/>"; 
    displayStr += "<b>Name:</b> " + item.name + "<br/>"; 
      
    for (j=0; j<item.properties.length; j++) {
      var property = item.properties[j];
      if (property.name == "Custom Image Upload" || property.name == "image") {
        item_imgs.push(property.value);
      } else {
        displayStr += "<b>" + property.name + ":</b> " + property.value + "<br/>"; 
      }
    }

    for (j=0; j<item_imgs.length; j++) {
      displayStr += '<div class="form-check">';
      displayStr +=   '<input class="form-check-input" type="checkbox" id= "cb-' + j + '"value="' + item_imgs[j] + '">';
      displayStr +=   '<label class="form-check-label" for="cb-' + j + '"><img width="200px" src="' + item_imgs[j] + '"/></label>';
      displayStr += '</div>';
    }

    displayStr += "</div>";
    $("#orderList").append(displayStr);

    // try and pre-fill
    var itemName = item.name.toLowerCase();
    if (pinataNameGuess == null 
    && itemName.includes("pinata")
    && ! itemName.includes("buster")
    && ! itemName.includes("blindfold")
    && ! itemName.includes("pullstring")) {

      pinataNameGuess = item.title;
      pinataQtyGuess = item.quantity;
    }
  }

  $("#pinata").val(pinataNameGuess);
  $("#qty").val(pinataQtyGuess);

  $(":submit").click(function() {
    // new lines fuck up the csv, get rid of them
    $("#notes").text($("#notes").text().replaceAll("\n", "<NEW_LINE>"));
    var imgs = []
    $(".form-check-input:checkbox:checked").each( function() {
      imgs.push($(this).val());
    });
    $("#imgs").val(imgs);
  });
};
