#include <pebble.h>
#include "digits.h"

static Window *s_window;
static Layer *s_layer;

static void update_layer(Layer* layer, GContext* ctx) {
  GRect bounds = layer_get_bounds(layer);
  graphics_context_set_fill_color(ctx, GColorBlack);
  graphics_fill_rect(ctx, bounds, 0, GCornerNone);
  graphics_context_set_stroke_color(ctx, GColorWhite);
  graphics_context_set_stroke_width(ctx, 5);

  int num_step = 60;
  int num_harmonics = sizeof(harmonics) / sizeof(Harmonic);
  GPoint orig;
  GPoint prev;
  GPoint s;
  for (int step = 0; step < num_step; step++) {
    s = GPoint(bounds.origin.x, bounds.origin.y);
    for (int h_idx = 0; h_idx < num_harmonics; h_idx++) {
      Harmonic* h = harmonics + h_idx;
      int phase = step * TRIG_MAX_ANGLE * h->freq / num_step + h->phase;
      s.x += h->amp * cos_lookup(phase) / (10 * TRIG_MAX_RATIO);
      s.y += h->amp * sin_lookup(phase) / (10 * TRIG_MAX_RATIO);
    }

    if (step == 0) {
      orig = s;
    } else {
      graphics_draw_line(ctx, prev, s);
    }
    prev = s;
  }
  graphics_draw_line(ctx, s, orig);
}

static void tick_handler(struct tm* now, TimeUnits units_changed) {
  if (s_layer) layer_mark_dirty(s_layer);
}

static void window_load(Window* window) {
  Layer* window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);
  s_layer = layer_create(bounds);
  layer_set_update_proc(s_layer, update_layer);
  layer_add_child(window_layer, s_layer);
  tick_timer_service_subscribe(MINUTE_UNIT, tick_handler);
}

static void window_unload(Window *window) {
  if (s_layer) layer_destroy(s_layer);
}

static void init(void) {
  s_window = window_create();
  window_set_window_handlers(s_window, (WindowHandlers) {
    .load = window_load,
    .unload = window_unload,
  });
  window_stack_push(s_window, true);
}

static void deinit(void) {
  window_destroy(s_window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}
