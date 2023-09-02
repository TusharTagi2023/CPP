function openCaseDetailPage(table_name){
    console.log("HEREE")
    window.location.replace('/table/'+table_name+'/')
  }


function open_edit_popup(event, data, table_name){
    event.preventDefault()
    $.ajax({
        type: 'GET',
        url: "/get_table_info/?data="+data+"&table_name="+table_name,
        success: function (data) {
                $('#popup_data_body').html('');
                $('#popup_data_body').append(data['body']);

                $('#popup_data_footer').html('');
                $('#popup_data_footer').append(data['footer'])
            },
        error: function (response) {
            alert("Please add atleast 1 step");
            }
        }
    ) 
}
