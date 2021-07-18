var csrfmiddlewaretoken = $("nav.performancesNav input[name='csrfmiddlewaretoken']").val()
var numberOfLinesInMessage = 8

$("#PerfEmtpyBase").on('click', function(event) {perfEmptyBase(true)})
$("#PerfPopulateBase").on('click', function(event) {perfPopulateBase(true, "empty")})
$("#VisualizeRef").on('click', function(event) {visualizeRef()})

function perfEmptyBase (start) {
  if (start) {
    $("div.loader").css({display:'block'})
    $('section').empty()
  }
  $.ajax({
    url : "visio/performances/",
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
    url : "visio/performances/",
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

function Employee ( name, position, salary, office ) {
  this.name = name;
  this.position = position;
  this.salary = salary;
  this._office = office;

  this.office = function () {
      return this._office;
  }
};

function visualizeRef () {
  $('section').empty()
  $('section').prepend('<table id="table_id" class="display">')
  data = [
    {
        "name":       "Tiger Nixon",
        "position":   "System Architect",
        "salary":     "$3,120",
        "start_date": "2011/04/25",
        "office":     "Edinburgh",
        "extn":       "5421"
    },
    {
        "name":       "Garrett Winters",
        "position":   "Director",
        "salary":     "$5,300",
        "start_date": "2011/07/25",
        "office":     "Edinburgh",
        "extn":       "8422"
    }
  ]

  columns = [
    { data: 'name' },
    { data: 'position' },
    { data: 'salary' },
    { data: 'office' }
]

  // columns = ['name', 'position', 'salary', 'office']
  console.log(columns)
  $('#table_id').DataTable(
    {
      data: data,
      columns: columns
  }
  );
}
