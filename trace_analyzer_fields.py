


class TraceAnalyzerFields:
    treename = "pspmt"
    energy_loss = "pid_vec_.pin_0_energy"
    energy_loss_range = (0, 10000)
    
    particle_ToF = "pid_vec_.tac_1"
    ToF_range = (160, 1600)

    beta_x = "high_gain_.pos_x_"
    beta_y = "high_gain_.pos_y_"

    ion_x = "low_gain_.pos_x_"
    ion_y = "low_gain_.pos_y_"

    implant_require = "low_gain_.energy_ > 0"
    rear_ion_veto = "(rit_b1_.energy_ < 0 || rit_b2_.energy_ < 0)"
    front_ion_require = "(fit_b1_.energy_ > 0 || fit_b2_.energy_ > 0)"

    clover_energy = "clover_vec_.energy"
    clover_time   = "clover_vec_.time"
    clover_high   = "clover_vec_.cloverHigh"
    event_time    = "high_gain_.time_"
    gamma_relative_time = f"{clover_time} - {event_time} - GetBetaGammaWalk({clover_energy})"

    