/*
Name:           roster_selector.js
Description:    get the server & storage and networks on call person for a
                given week as per the entry in the on call database.
Author:         Mark Larsen (initial 08/12/2017)
*/
$(document).ready(function()
{
  $('select[name = "roster_date"]').change(function()
  {
    //variables we need to pass an ajax post
    var selected_date = $('select[name = "roster_date"] option:selected').text();
    var sel_date_val = $('select[name = "roster_date"] option:selected').val();

    // this function will get the CSRFToken cookie
    function getCookie(name)
    {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '')
      {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++)
        {
          var cookie = $.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '='))
          {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
         }
       }
       return cookieValue;
     }

     function csrfSafeMethod(method)
     {
       // these HTTP methods do not require CSRF protection
       return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
     }

    //create a variable containing the CSRFToken
     var csrf_token = getCookie('csrftoken');

     //set up ajax with the csrf token
     $.ajaxSetup({
       crossDomain: false, // obviates need for sameOrigin test
       beforeSend: function(xhr, settings)
       {
         if (!csrfSafeMethod(settings.type))
         {
           xhr.setRequestHeader("X-CSRFToken", csrf_token);
         }
       }
     });

    // create a varibale with the data we intend to send via the GET request
    var send_data = {'selected_date': selected_date,
                     'csrfmiddlewaretoken': csrf_token,
                     'selected_date_val': sel_date_val,
                     };

    //var return_first;
    var oss_person_id;
    var nw_person_id;
    var es_person_id;

    function callback(response)
    {
      //console.log(response);
      $.each(JSON.parse(response), function(key,value)
      {
        oss_person_id = value[0];
        nw_person_id = value[1];
        es_person_id = value[2];

        if (oss_person_id == "1")
        {
          $('select[name = "oss_person"] option[value=""]').prop("selected", true);
        }
        else {
               $('select[name = "oss_person"] option[value="' + oss_person_id +'"]').prop("selected", true);
        }
        if (nw_person_id == "1")
        {
          $('select[name = "nw_person"] option[value=""]').prop("selected", true);
        }
        else {
               $('select[name = "nw_person"] option[value="' + nw_person_id +'"]').prop("selected", true);
        }
        if (es_person_id == "1")
        {
          $('select[name = "es_person"] option[value=""]').prop("selected", true);
        }
        else {
               $('select[name = "es_person"] option[value="' + es_person_id +'"]').prop("selected", true);
        }
        //console.log("Current Oncall - oss_person_id: " + value[0], "es_person_id: " + value[2], "nw_person_id: " + value[1]);
      })
    }

    //ajax call to send get request and return the ids for the Server & Network
    //on call people.
    $.ajax({ url: '/ajax_return_oncall/',
             type: 'GET',
             cache: false,
             data: send_data,
             success: function(response)
                      {
                        callback(response);
                      },
             error: function(obj, status, err)
                    {
                        alert(err); console.log(err);
                     },
      });
      //ajax request to get change_log entries for a given roster_id
      // as selected in the roster date drop down.
      $.ajax({ url: '/ajax_return_changelog/',
               type: 'GET',
               cache: false,
               data: send_data,
               success: function(data)
                        {
                          callback2(data);
                        },
               error: function(obj, status, err)
                      {
                          alert(err); console.log(err);
                       },
      });


      function callback2(data)
      {
        $('#changelog > tr').remove();
        $('#changelog').find('tbody').append('<tr></tr>');
        $.each(JSON.parse(data), function(key,value)
        {
          if (value[0])
          {

            var t = value[0].split(/[- : T]/);
            var d = new Date(t[0], t[1]-1, t[2], t[3], t[4], t[5]).toString();
            //only get the date and time we don't need the GMT or Timezone.
            d =  d.split(' ').slice(0, 5).join(' ');
          }
          
          //console.log(d, "oss_person_id " + value[1], "nw_person_id: " + value[2], "es_person_id: " + value[3])
          $('#changelog').find('tbody:last').after('<tr><td>' + d + '</td><td>' + value[1] + '</td><td>' + value[2] +  '</td><td>' + value[3] + '</td></tr>');
        });
      }
  }).trigger('change');
});


