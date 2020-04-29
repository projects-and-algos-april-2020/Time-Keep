$(document).ready(function(){
  console.log("attached jquery")
  $('h1').click(function(){
      $(this).css("background-color","green")
      $(this).css("color","white")
  })
  $('.reg_email').keyup(function(){
      $.ajax({
          url: "/email",
          method: "POST",
          data: $('.reg_form').serialize()
      })
      .done(function(res){
          console.log(res);
          $('.email').html(res)
      })
  })
  $('.submit_btn').click(function(){   // listen for when the #submit_btn element is clicked
      $.ajax({
            url: '/add_user',
            method: 'POST',
            data: $('.reg_form').serialize()
      })
      .done(function(response){
          console.log(response);
      })
      return false;                     // return false to disable the normal submission of the form
  });

})

$('#sw-go').click(function(){
$.ajax({
    url: '/start_time',
    method: 'POST',
    data: $('#sw_form').serialize()
})
.done(function(response){
    console.log(response);
})
return false;          // return false to disable the normal submission of the form
});

$('#sw-rst').click(function(){
    $.ajax({
        url: '/stop_time',
        method: 'POST',
        data: $('#sw_form').serialize()
    })
    .done(function(response){
        console.log(response);
    })
    return false;          // return false to disable the normal submission of the form
    });