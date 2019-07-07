function getTableData(data){
  let tableData = "<thead> <tr> <th>Block Number </th> <th>Name</th> <th>Cost (Wei)</th> <th>Log Index</th> <th>Expires </th> </tr> </thead><tbody>";
    $.each(data, function(key, value){

        tableData += '<tr>';
        tableData += '<td>'+value.blockNumber+'</td>';
        tableData += '<td>'+value.name+'</td>';
        tableData += '<td>'+value.cost+'</td>';
        tableData += '<td>'+value.logIndex+'</td>';
        tableData += '<td>'+new Date(value.expires * 1000)+'</td>';
        tableData += '<tr>';
  });
  tableData += '</tbody>'
  return tableData;
}

$("#action").click(function(e){
  $("#events").empty();
  $(".progress").show();

  $.getJSON( "/api/data/", {
       address: $("#addressId").val(),
       event_name: $("#eventName").val()
     })
       .done(function( data, textStatus, resp ) {
         if(resp.status !== 200) {
           M.toast({html: "No Data found", classes: 'rounded'});
           return;
        }
        tableData = getTableData(data);
         $('#events').append(tableData);
       })
       .fail(function( resp, textStatus, error ) {
           if (resp.responseJSON) {
             error += " , " + resp.responseJSON.error
           }
           M.toast({html: error, classes: 'rounded'});
       })
       .always(function() {
           $(".progress").hide();
       });
});
