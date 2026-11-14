// TH14 funcCall 3/4: reuse the existing engine-level set_player_hitbox(fx).
// The caller supplies this training card's normal player radius; do not guess it.
// At source call time: begin(base); spawn grow(base, target); then keep the boss script running.
// The spawned grow task first runs next frame, writes t=1..120, and finishes.
// Keep its lifetime within the attack; reset after the grow task has ended/stopped.
sub th14_player_scale_begin(base_radius: fx) {
    set_player_hitbox(base_radius * 3.6fx);
}

async sub th14_player_scale_grow(base_radius: fx, target_scale: fx) {
    for frame in 1..121 {
        var scale: fx = 1fx + (target_scale - 1fx) * (frame as fx) / 120;
        set_player_hitbox(base_radius * 3.6fx * scale);
        wait(1);
    }
}

sub th14_player_scale_reset(base_radius: fx) {
    set_player_hitbox(base_radius);
}
