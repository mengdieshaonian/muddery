
var controller = {

    // Set player's inventory
    setSkills: function(skills) {
        this.clearItems();
        
        var container = $("#skill_list");
        var item_template = container.find("tr.template");
        for (var i in skills) {
            var obj = skills[i];
            var item = item_template.clone()
	            .removeClass("template");
            
            var name = obj["name"];
            item.find(".skill_name")
                .data("dbref", obj["dbref"])
            	.text(name);
            
            if (obj["icon"]) {
            	var icon = settings.resource_location + obj["icon"];
            	item.find(".img_icon").attr("src", icon);
            }
            else {
            	item.find(".skill_icon").hide();
            }

			var desc = "";
            try {
            	desc = text2html.parseHtml(obj["desc"]);
            }
			catch(error) {
                console.error(error.message);
    	    }
            item.find(".skill_desc").html(desc);
            
			item.appendTo(container);
        }
    },
    
    clearItems: function() {
    	// Remove items that are not template.
    	$("#tab_skills tbody").children().not(".template").remove();
    },
    
    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        parent.commands.doLook(dbref);
    },
};
