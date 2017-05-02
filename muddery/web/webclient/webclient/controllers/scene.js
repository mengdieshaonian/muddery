
var controller = {

    clearScene: function() {
        ///////////////////////
        // clear scene box
        ///////////////////////

        $("#name_content").empty();
        $("#desc_content").empty();
        
        this.clearItems("#commands_content");
        this.clearItems("#things_content");
        this.clearItems("#npcs_content");
        this.clearItems("#players_content");

        for (var i = 0; i < 9; ++i) {
            this.clearItems("#exits_" + i);
            $("#link_" + i).hide();
        }
    },

    setScene: function(scene) {
        ///////////////////////
        // set scene box
        ///////////////////////

        this.clearScene();

        // add room's dbref
        var dbref = "";
        if ("dbref" in scene) {
            dbref = scene["dbref"];
        }
        $("#box_scene").data("dbref", dbref);

        // add room's name
        var room_name = "";
        try {
            room_name = text2html.parseHtml(scene["name"]);
        }
        catch(error) {
            console.error(error.message);
        }
        $("#name_content").html("&gt;&gt;&gt;&gt;&gt; " + room_name +  " &lt;&lt;&lt;&lt;&lt;");

        // add room's desc
        var room_desc = "";
        try {
            room_desc = text2html.parseHtml(scene["desc"]);
        }
        catch(error) {
            console.error(error.message);
        }
		$("#desc_content").html(room_desc);

        // add commands
        var contents = "cmds" in scene ? scene["cmds"]: null;
        this.addButtons("#commands", "#commands_content", contents);

        // add things
        contents = "things" in scene ? scene["things"]: null;
        this.addLinks("#things", "#things_content", contents);

        // add NPCs
        contents = "npcs" in scene ? scene["npcs"]: null;
        this.addLinks("#npcs", "#npcs_content", contents);

        // add players
        contents = "players" in scene ? scene["players"]: null;
        this.addLinks("#players", "#players_content", contents);

        // add exits
        // sort exits by direction
        var map = parent.map;
        var room_exits = [];
        if ("exits" in scene) {
            for (var i in scene["exits"]) {
                var direction = map.getExitDirection(scene.exits[i].key);
                // sort from north (67.5)
                if (direction < 67.5) {
                    direction += 360;
                }
                room_exits.push({"data": scene.exits[i],
                                 "direction": direction
                                 });
            }

            room_exits.sort(function(a, b) {return a.direction - b.direction;});
        }
        
        var exit_grids = [[], [], [] ,[] ,[], [], [], [], []];
        for (var i in room_exits) {
        	var index = map.getDirectionIndex(room_exits[i]["direction"]);
        	exit_grids[index].push(room_exits[i]["data"]);
        }
        
        // reverse the upper circle elements
        for (var i = 0; i < 4; ++i) {
        	exit_grids[i].reverse();
        }

        // add exits to table
        for (var i in exit_grids) {
            var grid_id = "#exits_" + i;
            var link_id = "#link_" + i;
            this.addLinks(link_id, grid_id, exit_grids[i]);
        }

        // If the center grid is empty, show room's name in the center grid.
        if (exit_grids[4].length == 0) {
            this.addText("", "#exits_4", room_name);
        }

        // set background
        var backview = $("#box_scene");
        if ("background" in scene && scene["background"]) {
            var url = settings.resource_location + scene["background"];
            backview.css("background", "url(" + url + ") no-repeat center center");
        }
        else {
            backview.css("background", "");
        }
    },
        
    clearItems: function(item_id) {
    	// Remove items that are not template.
    	$(item_id).children().not(".template").remove();
    },

    addButtons: function(block_id, content_id, data) {
    	var content = $(content_id);
		var item_template = content.find("input.template");

		var has_button = false;
		if (data) {
            for (var i in data) {
                var cmd = data[i];

                try {
                    var name = text2html.parseHtml(cmd["name"]);
                    item_template.clone()
                        .removeClass("template")
                        .data("cmd_name", cmd["cmd"])
                        .data("cmd_args", cmd["args"])
                        .html(name)
                        .appendTo(content);

                    has_button = true;
                }
                catch(error) {
                    console.error(error.message);
                }
            }
        }

		if (block_id) {
			if (has_button) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },
    
    addLinks: function(block_id, content_id, data, command) {
    	var content = $(content_id);
		var item_template = content.find("a.template");

		var has_link = false;
		if (data) {
            for (var i in data) {
                var obj = data[i];

                try {
                    var name = text2html.parseHtml(obj["name"]);
                    if ("complete_quest" in obj && obj["complete_quest"]) {
                        name += "[?]";
                    }
                    else if ("provide_quest" in obj && obj["provide_quest"]) {
                        name += "[!]";
                    }

                    item_template.clone()
                        .removeClass("template")
                        .data("dbref", obj["dbref"])
                        .html(name)
                        .appendTo(content);

                    has_link = true;
                }
                catch(error) {
                    console.error(error.message);
                }
            }
        }

		if (block_id) {
			if (has_link) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },

    addText: function(block_id, content_id, text) {
    	var content = $(content_id);
		var item_template = content.find("span.template");

		var has_text = false;
		if (text) {
            try {
                item_template.clone()
                    .removeClass("template")
                    .html(text)
                    .appendTo(content);

                has_text = true;
            }
            catch(error) {
                console.error(error.message);
            }
        }

		if (block_id) {
			if (has_text) {
				$(block_id).show();
			}
			else {
				$(block_id).hide();
			}
		}
    },

    doCommandLink: function(caller) {
        var cmd = $(caller).data("cmd_name");
        var args = $(caller).data("cmd_args");
        parent.commands.doCommandLink(cmd, args);
    },

    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        parent.commands.doLook(dbref);
    },

    doGoto: function(caller) {
        var dbref = $(caller).data("dbref");
        parent.commands.doGoto(dbref);
    },
};