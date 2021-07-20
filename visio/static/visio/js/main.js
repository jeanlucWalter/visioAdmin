var csrfmiddlewaretoken = $("nav.performancesNav input[name='csrfmiddlewaretoken']").val()
var numberOfLinesInMessage = 20

$("#PerfEmtpyBase").on('click', function(event) {perfEmptyBase(true)})
$("#PerfPopulateBase").on('click', function(event) {perfPopulateBase(true, "empty")})
$("#VisualizePdv").on('click', function(event) {visualizePdv()})
$("#VisualizeVentes").on('click', function(event) {visualizeVentes()})

function perfEmptyBase (start) {
  if (start) {
    $("div.loader").css({display:'block'})
    $('section').empty()
  }
  $.ajax({
    url : "/visio/performances/",
    type : 'get',
    data : {"action":"perfEmptyBase", "csrfmiddlewaretoken":csrfmiddlewaretoken, 'start':start},
    success : function(response) {
      console.log(response)
      if (response['errors'].length != 0) {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>Error : '+ response["errors"][0] + '</p>')
        $("div.loader").css({display:'none'})
      } else {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>'+ response["message"] + '</p>')
        if (!response['end']) {
          perfEmptyBase (false)
        } else {
          $("div.loader").css({display:'none'})
        }
      }
    },
    error : function(response) {
      console.log(response)
      $("div.loader").css({display:'none'})
    }
  })
}

function perfPopulateBase (start, method) {
  if (start && method == "empty") {
    $('section').empty()
    $("div.loader").css({display:'block'})
  }
  $.ajax({
    url : "/visio/performances/",
    type : 'get',
    data : {"action":"perfPopulateBase", 'method':method, 'start':start, "csrfmiddlewaretoken":csrfmiddlewaretoken},
    success : function(response) {
      console.log(response)
      if (response['errors'].length != 0) {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>Error : '+ response["errors"][0] + '</p>')
        $("div.loader").css({display:'none'})
      } else {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>'+ response["message"] + '</p>')
        if (response['query'] == "emptyDatabase") {
          if (response['end']) {
            perfPopulateBase (true, "populate")
          } else {
            perfPopulateBase (false, "empty")
          }
        } else {
          if (response['end']) {
            $("div.loader").css({display:'none'})
          } else {
            perfPopulateBase (false, "populate")
          }
        }
      }
    },
    error : function(response) {
      console.log(response)
      $("div.loader").css({display:'none'})
    }
  })
}

function visualizePdv () {
  visualizeGeneric('Pdv')
}

function visualizeVentes () {
  visualizeGeneric('Ventes')
}



function visualizeGeneric(table) {
  $('section').empty()
  $("div.loader").css({display:'block'})
  $.ajax({
    url : "/visio/performances/",
    type : 'get',
    data : {"action":"perfImport"+table, "csrfmiddlewaretoken":csrfmiddlewaretoken},
    success : function(response) {
      console.log(response['titles'])
      columnsTitle = []
      $.each(response['titles'], function( _, value ) {
        columnsTitle.push({title: value})
      })
      buildTable (columnsTitle, response['values'], 'table' + table)
      $("div.loader").css({display:'none'})
    },
    error : function(response) {
      console.log(response)
      $("div.loader").css({display:'none'})
    }
  })
}

function buildTable (columnsTitle, values, tableId) {
  $('section').empty()
  $('section').prepend('<table id="'+tableId+'" class="display" style="width:100%">')
  $('#'+tableId).DataTable(
    {"scrollX": true, data: values, columns: columnsTitle}
  )
}

