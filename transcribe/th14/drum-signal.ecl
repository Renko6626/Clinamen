// TH14 funcCall 6: one drum cue releases each waiting bullet once.
// The attack owns `channel` (0..7) and calls pulse_signal(channel) at the original drum times.
// Native source has no competing continuous turn/acceleration on these bullets.
// rand is sampled per bullet at release, not once when the shooter is configured.
xformdef TH14_DRUM_ONCE(channel: int) {
    wait_signal(channel);
    @60 set_accel(at_effect(((rand(65536) - 32768) as fx) / 32768 * 0.01fx));
    set_accel(0fx);
}
