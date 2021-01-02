import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Cube Remote App
#
# Args:
#

class CubeRemote(hass.Hass):


##  INITIALIZE STUFF
    def initialize(self):
      
        self.myDebug = 0
        self.myNotify ="sonytv"		# - no screen notification
        self.myGestures = [ "0 Awake"
                     , "1 Shake"
                     , "2 Free fall"
                     , "3 Flip 90"
                     , "4 Flip 180"
                     , "5 Move on any side"
                     , "6 Double tap on any side"
                     , "7 Turn clockwise"
                     , "8 Turn counter Clockwise"
                     ]

        self.my_active_last ="-"
        self.my_active_current ="-"
        self.my_gesture_last ="-"
        self.my_gesture_current ="-"
        self.my_event_last ="-"
        self.my_event_current ="-"
        self.my_remote_current ="-"
        self.my_player_last ="-"

##########################################################################################                             
## 
##   array's of light to change brightness
## 
##########################################################################################                             
        # 'Light Wohnzimmer'
        self.lightsWohnzimmer = [ 'light.wohnzimmer_licht_1'
                                      ,'light.wohnzimmer_licht_2' 
                                      ,'light.wohnzimmer_licht_3' 
                                      ,'light.wohnzimmer_licht_4' 
                                      ,'light.wand'
                                      ,'light.sideboard_rechts' 
                                      ,'light.sideboard_links' 
                                      ,'light.wohnzimmer_rechts' 
                                      ,'light.wohnzimmer_links'                       
                                      ]
        # 'Light Esszimmer'
        self.lightsEsszimmer  = [ 'light.kerze'
                                     ,'light.esszimmer_1' 
                                     ,'light.esszimmer_2' 
                                     ,'light.esszimmer_3' 
                                     ,'light.esszimmer_4' 
                                     ]

        # 'Light Schlafzimmer'
        self.lightsSchlafzimmer = [ 'light.bett_boden'
                                         ,'light.bett_boden_inks' 
                                         ,'light.bett_kissen' 
                                         ,'light.schlafzimmer_decke_1'
                                         ,'light.schlafzimmer_decke_2'
                                 ]

        self.version = "0.0.1"
        self.log("You are now ready to run Apps!")
        self.notify(    title="starting CubeRemote v" + self.version
             , message="Hello - starting CubeRemote"
             , name="sonytv" 
             , data =  { "fontsize" : "large"
                        , "position" : "top-left"
                        , "duration" : "4"
                        , "transparancy" : "90"
                        , "color" : "green"
                        } )

        self.listen_event_handle_list = []
        self.timer_handle_list = []
        self.actor_single = self.args.get("actor_single")
        self.actor_double = self.args.get("actor_double")
        self.actor_hold = self.args.get("actor_hold")
        # self.id = self.args["id"]
        self.dimmer_timer_handle = None

        self.listen_event_handle_list.append(
            self.listen_event(self.event_detected, "deconz_event")
        )

##  TERMINATE LISTENER
    def terminate(self):
        for listen_event_handle in self.listen_event_handle_list:
            self.cancel_listen_event(listen_event_handle)

        for timer_handle in self.timer_handle_list:
            self.cancel_timer(timer_handle)

##  ANALYZE EVENTS
    def event_detected(self, event_name, data, kwargs):

        # if data["id"] == self.id:
		#self.id = data['id']
		#self.event = data.['event']
		#self.device_id = data.['device_id']
		#self.gesture = data.['gesture']

        if self.myDebug == 1:
            data_got = "ID: %s gesture: %s event: %s \ndevice_id: %s unique_id: %s " % (data['id'],self.myGestures[data['gesture']],data['event'],data['device_id'],data['unique_id'] )
            self.log("Got Event:" + data_got)
            self.notify( title="got event" +  data['id']
                     , message="smile"
                     , name="sonytv" 
                     , data =  { "fontsize" : "large"
                                       , "position" : "top-left"
                                       , "duration" : "4"
                                       , "transparancy" : "90"
                                       , "color" : "green"
                                       } )

        self.my_entity_id = data['id']
        self.my_gesture   = data['gesture']
        self.my_event     = data['event']

## get old status and save new status
        ## 1.    now backup old states of entity_id ##############################################
        self.my_active_last = self.my_active_current
        self.my_active_current = self.my_entity_id

        ## 2.    now backup old states of gesture ################################################
        self.my_gesture_last = self.my_gesture_current
        self.my_gesture_current = self.my_gesture

        ## 3.    now backup old states of event ##################################################
        self.my_event_last = self.my_event_current
        self.my_event_current = self.my_event

        self.my_remote = self.my_remote_current

            
        self.myNewAction = "-"
        if self.my_gesture == 0 and self.my_event == 7000:					# wakeup
            self.my_remote = "wakeup"
            self.myNewAction = "-"
        elif self.my_gesture == 1 and self.my_event == 7007:					# shake
            self.my_remote = "Stop/Play"
            self.myNewAction="Stop/Play"
        elif self.my_gesture == 2 and self.my_event == 7008:					# free fall
            self.my_remote = "Reset"
            self.myNewAction = "-"
        elif self.my_gesture == 7:										# turn clockwise
            self.myNewAction = "turn"
        elif self.my_gesture == 8:										# turn counter clockwise
            self.myNewAction = "turn"
        elif self.my_gesture == 3:										# Flip90
            if self.my_event == 1002 and self.my_event_last == 2001:
                self.my_remote = "Media Wohnzimmer"
                self.myNewAction = "select"
            elif self.my_event == 1003 and self.my_event_last == 3001:
                self.my_remote = "Media Schlafzimmer"
                self.myNewAction = "select"
            elif self.my_event == 1004 and self.my_event_last == 4001:
                self.my_remote = "Media Amplifier"
                self.myNewAction = "select"
            elif self.my_event == 1005 and self.my_event_last == 5001:
                self.my_remote = "Media Speaker Global"
                self.myNewAction = "select"
            elif self.my_event == 2001:
                self.my_remote = "Light Wohnzimmer"
                self.myNewAction = "select"
            elif self.my_event == 3001:
                self.my_remote = "Light Esszimmer"
                self.myNewAction = "select"
            elif self.my_event == 5001:
                self.my_remote = "Light Global"
                self.myNewAction = "select"
        else:
            # myNewRemote = my_remote_current
            self.myNewAction="turner"

        self.log('remote:{} Action:{} event:{} last_event:{}'.format(self.my_remote,self.myNewAction,self.my_event,self.my_event_last))
        if self.myDebug == 1:
            self.log("vars:" 
                        + "\n r: " + str(      self.my_remote ) 
                        + "\n g: " + str(      self.my_gesture ) 
                        + "\n ac:" + self.my_active_current 
                        + "\n al:" + self.my_active_last 
                        + "\n gc:" + str( self.my_gesture_current ) 
                        + "\n gl:" + str( self.my_gesture_last )
                        + "\n ec:" + str( self.my_event_current ) 
                        + "\n el:" + str( self.my_event_last ) 
                        )

        if self.myNewAction == "select":
            self.my_remote_current = self.my_remote
            if self.myNotify != "-":
                self.notify(    title = "select Remote"
                            , message = self.my_remote
                               , name = self.myNotify 
                          , data =  { "fontsize" : "large"
                                    , "position" : "top-left"
                                    , "duration" : "2"
                                    , "transparancy" : "90"
                                    , "color" : "green"
                                  } )

        self.action ="-"
##  prepare Lights to modify brightness !!!
        if self.myNewAction == "turn" and self.my_remote=="Light Wohnzimmer":
            self.my_entities = self.lightsWohnzimmer
            self.action ="Light"
        elif self.myNewAction == "turn" and self.my_remote=="Light Schlafzimmer":
            self.my_entities = self.Schlafzimmer
            self.action ="Light"
        elif self.myNewAction == "turn" and self.my_remote=="Light Esszimmer":
            self.my_entities = self.lightsEsszimmer
            self.action ="Light"
        elif self.myNewAction == "turn" and self.my_remote=="Light Global":
            self.my_entities = self.lightsWohnzimmer + self.lightsEsszimmer + self.lightsSchlafzimmer
            self.action ="Light"
  

## now calling our functions to change something .........................................
        if self.myNewAction == "Stop/Play":
            self.CallStopPlay( ) 
        elif self.action == "Light":
            self.CallLightShow( self.my_entities , self.my_event ) 


    def CallLightShow(self, entities , mod_brightness ):
        for entity_id in entities:
            on_off = self.get_state( entity_id )
            if on_off == "on":
                brightness = self.get_state( entity_id , "brightness")
                newbrightness = int( brightness ) + int( mod_brightness /200)
                if newbrightness <= 0:
                    newbrightness = 1
                elif newbrightness >=255:
                    newbrightness = 255     
                if brightness != newbrightness:
                    self.turn_on( entity_id , brightness = newbrightness , transition = 2)  # , color_name="sandy brown"

    def CallStopPlay(self ):
        # all_media_player = self.get_state(group, attribute = 'media_player')   #  self.entity_ids('media_player')
        if self.my_player_last != "-":
            last_player_arr = self.my_player_last.split(",")
        else:
            all_media_player = self.get_state( 'media_player' )
            self.my_player_last = ""
            for entity_id in all_media_player:
                cur_state = self.get_state( entity_id )
                if cur_state  == "playing":
                    if len( self.my_player_last ) > 0:
                        self.my_player_last = self.my_player_last + ","
                    self.my_player_last = self.my_player_last + entity_id
            last_player_arr = self.my_player_last.split(",")
        for entity_id in last_player_arr:
            if len(entity_id) > 2:
                # self.media_player(entity_id,'media_play_pause')
                self.call_service('media_player/media_play_pause',
                              entity_id=entity_id)
                
                
#                hass.services.call(    'media_player'
#                          , 'media_play_pause'
#                          , { "entity_id" : entity_id
#                          },False)


#     if player_action == "stop":
#     # save string of stopped players ...................
#       self.set_textvalue("input_text.cube_player_last", last_player_str)
#     else:
#       # save none ........................................
#       self.set_textvalue("input_text.cube_player_last", "none")

    def notused(self):


        # all_media_player = self.get_state(group, attribute = 'media_player')   #  self.entity_ids('media_player')
        all_media_player = self.get_state( 'media_player' )
        last_player_str = ""
        for entity_id in all_media_player:
            cur_state = self.get_state( entity_id )
            # self.log(' ent ::::::::::::' + entity_id + " - " + cur_state )
            if cur_state  == "playing":
                self.log(' ent ::::::::::::' + entity_id + " - " + cur_state )
                if len( last_player_str ) > 0:
                    last_player_str = last_player_str + ","
                last_player_str = last_player_str + entity_id
        last_player_arr = last_player_str.split(",")  


        for entity_id in last_player_arr:
            if len(entity_id) > 2:
                hass.services.call(    'media_player'
                          , 'media_play_pause'
                          , { "entity_id" : entity_id
                          },False)

#     if player_action == "stop":
#     # save string of stopped players ...................
#       self.set_textvalue("input_text.cube_player_last", last_player_str)
#     else:
#       # save none ........................................
#       self.set_textvalue("input_text.cube_player_last", "none")
     
  










       # cur_state = hass.get_state( entity_id )
#       if cur_state is None:
#         self.log('Could not get current state for {}.'.format( entity_id ) )
 #      else:
 #        self.log('Could not get current state for {}.' + entity_id  )
 #        if cur_state.state == "playing":
 #          if len( last_player_str ) > 0:
 #            #self.log('player playing :' . format( entity_id ) )
 #            last_player_str = last_player_str + ","
 #          last_player_str = last_player_str + entity_id
