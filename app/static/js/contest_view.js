  $('.js-add-stage').click(function(e) {
    $(form_stage).insertAfter(this);
    $('.js-add-stage').hide();
    let contest = $(this).attr('contest');
    $('#form-stage').submit(function(event) {
      event.preventDefault();
      let form = $(this)[0]
      let data = new FormData(form);
      $.ajax({
        type: "POST",
        url: `/add_stage/${contest}`,
        contentType: false,
        processData: false,
        data: data,
        success: function(data){
          location.reload();
        },
      });
      $('#form-stage').remove();
      $('.js-add-stage').show();
    });
    $('#form-stage-cancel').click(function() {
      $('#form-stage').remove();
      $('.js-add-stage').show();
    });
  });

  $('.js-del-contest').click(function() {
    $('#delModal').modal('show');
    let contest = $(this).attr('contest');
    $('#btn-delete').attr('href', `del_contest/${contest}`);
  });

  $('.js-edit-stage').click(function() {
    $(form_stage).insertAfter(this);
    let title = $(this).prevAll('a').text();
    let link = $(this).prevAll('a').attr('href');
    let deadline = $(this).prev('span').attr('deadline');
    $('#form-stage #title').val(title);
    $('#form-stage #link').val(link);
    $('#form-stage #deadline').val(deadline);
    $('.js-add-stage, .js-edit-stage, .js-del-stage').hide();
    let stage = $(this).attr('stage');
    $('#form-stage').submit(function(event) {
      event.preventDefault();
      let form = $(this)[0]
      let data = new FormData(form);
      $.ajax({
        type: "POST",
        url: `/edit_stage/${stage}`,
        contentType: false,
        processData: false,
        data: data,
        success: function(data){
          location.reload();
        },
      });
      $('#form-stage').remove();
      $('.js-add-stage, .js-edit-stage, .js-del-stage').show();
    });
    $('#form-stage-cancel').click(function() {
      $('#form-stage').remove();
      $('.js-add-stage, .js-edit-stage, .js-del-stage').show();
    });
  });

  $('.js-del-stage').click(function() {
    $('#delModal').modal('show');
    let stage = $(this).attr('stage');
    $('#btn-delete').attr('href', `del_stage/${stage}`);
  });

  $('#group-select').change(() => {
    let group = $( "#group-select option:selected" ).val();
    console.log(group);
//    $.get( "/", { group: group } );
    window.location.href = `/?group=${group}`;
  });