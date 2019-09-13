/*
Name:           update_toil.js
Description:    update the toil update form and change values in line with
                the rates of pay.  I know it's bad jQuery...but it seems to work ¯\_(ツ)_/¯
Author:         Mark Larsen (initial 28/08/2019)
*/
$(document).ready(function(){
    // update the totals whenever the form values are updated
    $(document).on('change', 'input', function() {
      // set total variables
      var toil1xtotal = 0;
      var toil15xtotal = 0;
      var toil2xtotal = 0;
      var toil25xtotal = 0;
      var toiltakentotal = 0;
      // set variables to match each of the id's in the form
      var toil1x = $('#id_toil_earned_1x').val();
      var toil15x = $('#id_toil_earned_1_5x').val();
      var toil2x = $('#id_toil_earned_2x').val();
      var toil25x = $('#id_toil_earned_2_5x').val();
      var toiltaken = $('#id_toil_taken').val();
      // only accept the value if it's not NaN and has a length thats not 0
      if (!isNaN(toil1x) && toil1x.length !== 0) {
        toil1xtotal += parseFloat(toil1x);
      }
      if (!isNaN(toil15x) && toil15x.length !== 0) {
        toil15xtotal += parseFloat(toil15x) * 1.5;
      }
      if (!isNaN(toil2x) && toil2x.length !== 0) {
        toil2xtotal += parseFloat(toil2x) * 2;
      }
      if (!isNaN(toil25x) && toil25x.length !== 0) {
        toil25xtotal += parseFloat(toil25x) * 2.5;
      }
      if (!isNaN(toiltaken) && toiltaken.length !== 0) {
        toiltakentotal += parseFloat(toiltaken);
      }

      // use the console.log entries below to debug
      //console.log("toil1x: " + toil1xtotal);
      //console.log("toil15x: " + toil15xtotal);
      //console.log("toil2x: " + toil2xtotal);
      //console.log("toil25x: " + toil25xtotal);
      //console.log("toiltaken: " + toiltakentotal);

      // create a variable and add together all the toil hours
      var toil_total = (toil1xtotal + toil15xtotal + toil2xtotal + toil25xtotal - toiltakentotal)
      $('#id_toil_total').val(toil_total);
    });   
});