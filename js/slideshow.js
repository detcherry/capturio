$(function(){
	var anAnimation = new Animation();
	anAnimation.init();
});

function Animation(){
	this.interval = 5000;
	this.previousPosition = "";
	this.currentPosition = "left";
}

Animation.prototype = {
	
	init: function(){
		var that = this;
		setInterval(function(){
			that.nextSlide();
		}, this.interval);
	},
	
	nextSlide: function(){
		
		if(this.currentPosition == "left"){
			this.previousPosition = "left";
			this.currentPosition = "center";
			newMargin = "-100%";			
		}
		else{
			if(this.currentPosition == "right"){
				this.previousPosition = "right";
				this.currentPosition = "center";
				newMargin = "-100%";
			}
			else{
				if(this.previousPosition == "left"){
					this.previousPosition = "center";
					this.currentPosition = "right";
					newMargin = "-200%";
				}
				else{
					this.previousPosition = "center";
					this.currentPosition = "left";
					newMargin = "0%";
				}
			}
		}
		
		/*
		if(this.currentPosition == "left"){
			this.currentPosition = "center";
			newMargin = "-100%";
		}
		else if(this.currentPosition == "center"){
				this.currentPosition = "right";
				newMargin = "-200%";				
		}
		else{
				this.currentPosition = "left";
				newMargin = "0%";
		}*/

		$("#slides_wrapper")
			.animate({
				'marginLeft':newMargin,
			},600);
		
		that = this
		setTimeout(function(){
			that.changeText(that.currentPosition);
			},350);
		
	},
	
	changeText: function(position){
		
		if(position == "left"){
			$("p#object").html("take a picture of my business card");
			$("p#vcard").html("receive instantly my vcard");			
		}
		else{
			if(position == "center"){
				$("p#object").html("take a picture of my t-shirt");
				$("p#vcard").html("receive instantly my contact info");
			}
			else{
				$("p#object").html("take a picture of her tattoo");
				$("p#vcard").html("and get in touch with her");				
			}
		}
	},
	
}