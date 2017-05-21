function checkAddress() {
  var street = $('#connRequest [name="street"]').val();
  var num = $('#connRequest [name="num"]').val();
  var url = $('#connRequest').attr('action') + '?street=' + street + '&num=' + num;
  var path = window.location.origin + url;
  window.location.assign(path);
}
