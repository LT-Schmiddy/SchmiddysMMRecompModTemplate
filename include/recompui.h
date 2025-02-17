#ifndef __RECOMPUI_H__
#define __RECOMPUI_H__

#include "modding.h"

typedef unsigned long RecompuiContext;
typedef unsigned long RecompuiResource;

// Height of the window in DP units. This is fixed regardless of window size and aspect ratio.
#define RECOMPUI_TOTAL_HEIGHT 1080.0f

typedef enum {
    CURSOR_NONE,
    CURSOR_POINTER
} RecompuiCursor;

typedef enum {
    EVENT_TYPE_NONE,
    EVENT_TYPE_CLICK,
    EVENT_TYPE_FOCUS,
    EVENT_TYPE_HOVER,
    EVENT_TYPE_ENABLE,
    EVENT_TYPE_DRAG,
    EVENT_TYPE_TEXT,
    EVENT_TYPE_UPDATE,
    EVENT_TYPE_COUNT
} RecompuiEventType;

typedef enum {
    DRAG_PHASE_NONE,
    DRAG_PHASE_START,
    DRAG_PHASE_MOVE,
    DRAG_PHASE_END
} RecompuiDragPhase;

typedef enum {
    DISPLAY_NONE,
    DISPLAY_BLOCK,
    DISPLAY_INLINE,
    DISPLAY_INLINE_BLOCK,
    DISPLAY_FLOW_ROOT,
    DISPLAY_FLEX,
    DISPLAY_INLINE_FLEX,
    DISPLAY_TABLE,
    DISPLAY_INLINE_TABLE,
    DISPLAY_TABLE_ROW,
    DISPLAY_TABLE_ROW_GROUP,
    DISPLAY_TABLE_COLUMN,
    DISPLAY_TABLE_COLUMN_GROUP,
    DISPLAY_TABLE_CELL
} RecompuiDisplay;

typedef enum {
    POSITION_ABSOLUTE,
    POSITION_RELATIVE
} RecompuiPosition;

typedef enum {
    JUSTIFY_CONTENT_FLEX_START,
    JUSTIFY_CONTENT_FLEX_END,
    JUSTIFY_CONTENT_CENTER,
    JUSTIFY_CONTENT_SPACE_BETWEEN,
    JUSTIFY_CONTENT_SPACE_AROUND,
    JUSTIFY_CONTENT_SPACE_EVENLY
} RecompuiJustifyContent;

typedef enum {
    FLEX_DIRECTION_ROW,
    FLEX_DIRECTION_COLUMN
} RecompuiFlexDirection;

typedef enum {
    ALIGN_ITEMS_FLEX_START,
    ALIGN_ITEMS_FLEX_END,
    ALIGN_ITEMS_CENTER,
    ALIGN_ITEMS_BASELINE,
    ALIGN_ITEMS_STRETCH
} RecompuiAlignItems;

typedef enum {
    OVERFLOW_VISIBLE,
    OVERFLOW_HIDDEN,
    OVERFLOW_AUTO,
    OVERFLOW_SCROLL
} RecompuiOverflow;

typedef enum {
    UNIT_PX,
    UNIT_DP,
    UNIT_PERCENT
} RecompuiUnit;

typedef enum {
    FONT_STYLE_NORMAL,
    FONT_STYLE_ITALIC
} RecompuiFontStyle;

typedef enum {
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_RIGHT,
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_JUSTIFY
} RecompuiTextAlign;

typedef enum {
    TEXT_TRANSFORM_NONE,
    TEXT_TRANSFORM_CAPITALIZE,
    TEXT_TRANSFORM_UPPERCASE,
    TEXT_TRANSFORM_LOWERCASE
} RecompuiTextTransform;

typedef enum {
    DRAG_NONE,
    DRAG_DRAG,
    DRAG_DRAG_DROP,
    DRAG_BLOCK,
    DRAG_CLONE
} RecompuiDrag;

typedef enum {
    TAB_INDEX_NONE,
    TAB_INDEX_AUTO
} RecompuiTabIndex;

typedef enum {
    BUTTONSTYLE_PRIMARY,
    BUTTONSTYLE_SECONDARY,
} RecompuiButtonStyle;

typedef struct {
    unsigned long type;
    float duration;
} RecompuiAnimation;

typedef struct {
    unsigned char r;
    unsigned char g;
    unsigned char b;
    unsigned char a;
} RecompuiColor;

#define RECOMPUI_NULL_CONTEXT (0xFFFFFFFFUL)
#define RECOMPUI_NULL_RESOURCE (0xFFFFFFFFUL)

// Contexts
RECOMP_IMPORT("*", RecompuiContext recompui_create_context());
RECOMP_IMPORT("*", void recompui_open_context(RecompuiContext context));
RECOMP_IMPORT("*", void recompui_close_context(RecompuiContext context));
RECOMP_IMPORT("*", RecompuiResource recompui_context_root(RecompuiContext context));
RECOMP_IMPORT("*", void recompui_show_context(RecompuiContext context));
RECOMP_IMPORT("*", void recompui_hide_context(RecompuiContext context));

// Resources
RECOMP_IMPORT("*", RecompuiContext recompui_create_style(RecompuiContext context));
RECOMP_IMPORT("*", RecompuiContext recompui_create_element(RecompuiContext context, RecompuiResource parent));
RECOMP_IMPORT("*", RecompuiContext recompui_create_button(RecompuiContext context, RecompuiResource parent, const char* text, RecompuiButtonStyle style));

// Position and Layout
RECOMP_IMPORT("*", void recompui_set_position(RecompuiResource id, RecompuiPosition position));
RECOMP_IMPORT("*", void recompui_set_left(RecompuiResource id, float left, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_top(RecompuiResource id, float top, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_right(RecompuiResource id, float right, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_bottom(RecompuiResource id, float bottom, RecompuiUnit unit));

// Sizing
RECOMP_IMPORT("*", void recompui_set_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_width_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_height(RecompuiResource id, float height, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_height_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_min_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_min_height(RecompuiResource id, float height, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_max_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_max_height(RecompuiResource id, float height, RecompuiUnit unit));

// Padding
RECOMP_IMPORT("*", void recompui_set_padding(RecompuiResource id, float padding, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_padding_left(RecompuiResource id, float padding, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_padding_top(RecompuiResource id, float padding, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_padding_right(RecompuiResource id, float padding, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_padding_bottom(RecompuiResource id, float padding, RecompuiUnit unit));

// Margins
RECOMP_IMPORT("*", void recompui_set_margin(RecompuiResource id, float margin, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_margin_left(RecompuiResource id, float margin, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_margin_top(RecompuiResource id, float margin, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_margin_right(RecompuiResource id, float margin, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_margin_bottom(RecompuiResource id, float margin, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_margin_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_margin_left_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_margin_top_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_margin_right_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_margin_bottom_auto(RecompuiResource id));

// Borders
RECOMP_IMPORT("*", void recompui_set_border_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_left_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_top_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_right_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_bottom_width(RecompuiResource id, float width, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_radius(RecompuiResource id, float radius, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_top_left_radius(RecompuiResource id, float radius, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_top_right_radius(RecompuiResource id, float radius, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_bottom_left_radius(RecompuiResource id, float radius, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_border_bottom_right_radius(RecompuiResource id, float radius, RecompuiUnit unit));

// Colors
RECOMP_IMPORT("*", void recompui_set_background_color(RecompuiResource id, const RecompuiColor* color));
RECOMP_IMPORT("*", void recompui_set_border_color(RecompuiResource id, const RecompuiColor* color));
RECOMP_IMPORT("*", void recompui_set_border_left_color(RecompuiResource id, const RecompuiColor* color));
RECOMP_IMPORT("*", void recompui_set_border_top_color(RecompuiResource id, const RecompuiColor* color));
RECOMP_IMPORT("*", void recompui_set_border_right_color(RecompuiResource id, const RecompuiColor* color));
RECOMP_IMPORT("*", void recompui_set_border_bottom_color(RecompuiResource id, const RecompuiColor* color));
RECOMP_IMPORT("*", void recompui_set_color(RecompuiResource id, const RecompuiColor* color));

// Cursor and Display
RECOMP_IMPORT("*", void recompui_set_cursor(RecompuiResource id, RecompuiCursor cursor));
RECOMP_IMPORT("*", void recompui_set_opacity(RecompuiResource id, float opacity));
RECOMP_IMPORT("*", void recompui_set_display(RecompuiResource id, RecompuiDisplay display));

// Flexbox
RECOMP_IMPORT("*", void recompui_set_justify_content(RecompuiResource id, RecompuiJustifyContent justify_content));
RECOMP_IMPORT("*", void recompui_set_flex_grow(RecompuiResource id, float grow));
RECOMP_IMPORT("*", void recompui_set_flex_shrink(RecompuiResource id, float shrink));
RECOMP_IMPORT("*", void recompui_set_flex_basis_auto(RecompuiResource id));
RECOMP_IMPORT("*", void recompui_set_flex_basis(RecompuiResource id, float basis, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_flex_direction(RecompuiResource id, RecompuiFlexDirection flex_direction));
RECOMP_IMPORT("*", void recompui_set_align_items(RecompuiResource id, RecompuiAlignItems align_items));

// Overflow
RECOMP_IMPORT("*", void recompui_set_overflow(RecompuiResource id, RecompuiOverflow overflow));
RECOMP_IMPORT("*", void recompui_set_overflow_x(RecompuiResource id, RecompuiOverflow overflow));
RECOMP_IMPORT("*", void recompui_set_overflow_y(RecompuiResource id, RecompuiOverflow overflow));

// Text and Fonts
RECOMP_IMPORT("*", void recompui_set_font_size(RecompuiResource id, float size, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_letter_spacing(RecompuiResource id, float spacing, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_line_height(RecompuiResource id, float height, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_font_style(RecompuiResource id, RecompuiFontStyle style));
RECOMP_IMPORT("*", void recompui_set_font_weight(RecompuiResource id, unsigned long weight));
RECOMP_IMPORT("*", void recompui_set_text_align(RecompuiResource id, RecompuiTextAlign text_align));

// Gaps
RECOMP_IMPORT("*", void recompui_set_gap(RecompuiResource id, float size, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_row_gap(RecompuiResource id, float size, RecompuiUnit unit));
RECOMP_IMPORT("*", void recompui_set_column_gap(RecompuiResource id, float size, RecompuiUnit unit));

// Drag and Focus
RECOMP_IMPORT("*", void recompui_set_drag(RecompuiResource id, RecompuiDrag drag));
RECOMP_IMPORT("*", void recompui_set_tab_index(RecompuiResource id, RecompuiTabIndex focus));

#endif
