from dispatcher.event_dispatcher import post_event

def obs_hangry_cat_activate():
                                            
                # mute peekBoard
                # activate hangry-cat
                # steal fish
                # timer.start
                # add timer-queue for hangry-cat deactivate && peekBoard reactivate
    post_event("obs_set_input_mute", {"audiosource":"peekBoard", "muted":True })
    # write file with victim of stolen fish
    post_event("obs_set_source_visibility", {"scene_name": "ALERTS", "source_name": "cat_lul"})

    pass

def obs_hangry_cat_deactivate():
    pass
