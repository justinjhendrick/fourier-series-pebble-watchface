#include <pebble.h>
#include "digits.h"

static Window *s_window;
static Layer *s_layer;

static void draw_digit(GContext* ctx, GPoint tl, Harmonic* harmonic, int num_harmonics) {
  if (num_harmonics == 0) return;
  int num_step = 40;
  GPoint orig;
  GPoint prev;
  GPoint s;
  for (int step = 0; step < num_step; step++) {
    s = tl;
    for (int h_idx = 0; h_idx < num_harmonics; h_idx++) {
      Harmonic* h = harmonic + h_idx;
      int phase = step * TRIG_MAX_ANGLE * h->freq / num_step + h->phase;
      s.x += h->amp * cos_lookup(phase) / (20 * TRIG_MAX_RATIO);
      s.y += h->amp * sin_lookup(phase) / (12 * TRIG_MAX_RATIO);
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

static void update_layer(Layer* layer, GContext* ctx) {
  GRect bounds = layer_get_bounds(layer);
  graphics_context_set_fill_color(ctx, GColorBlack);
  graphics_fill_rect(ctx, bounds, 0, GCornerNone);
  graphics_context_set_stroke_color(ctx, GColorWhite);
  graphics_context_set_stroke_width(ctx, 5);
  GRect main = grect_inset(bounds, GEdgeInsets(3));
  int w = main.size.w / 5;
  int h = main.size.h / 2;

  GPoint tl = main.origin;
  draw_digit(ctx, tl, B0, sizeof(B0) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B1, sizeof(B1) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B2, sizeof(B2) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B3, sizeof(B3) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B4, sizeof(B4) / sizeof(Harmonic));

  tl.y += h;

  tl.x = main.origin.x;
  draw_digit(ctx, tl, B5, sizeof(B5) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B6, sizeof(B6) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B7, sizeof(B7) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B8, sizeof(B8) / sizeof(Harmonic));
  tl.x += w;
  draw_digit(ctx, tl, B9, sizeof(B9) / sizeof(Harmonic));
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
