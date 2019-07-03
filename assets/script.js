

var stop = false;
var t=setInterval(animateRadio,500)

function animateRadio(){
	var labels = document.getElementsByClassName("labelR");
	if(typeof labels !="undefined" && !stop){
		stop = true;
		labels[0].classList.add("active");
	var updateLabel = function(e) {
  if (event.target.type === "radio") {
    return;
  }
  
  var labels = document.getElementsByClassName("labelR");
  for (i = 0; i < labels.length; i++) {
    if (event.target.type === "radio") {
      continue;
    }
    
    if (e.target === labels[i]) {
	  labels[i].classList.add("active");
    } else {
       labels[i].classList.remove("active");
    }
  }
}

var radioLabels = document.getElementsByClassName("radioTrack");
for (i = 0; i < radioLabels.length; i++) {
  radioLabels[i].addEventListener("click", updateLabel, false);
}

}
}