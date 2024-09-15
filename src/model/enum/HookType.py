from enum import Enum


class HookType(Enum):

    H_SLIDESHOW_CONTENT_TOOLBAR_ACTIONS_START = 'h_slideshow_toolbar_actions_start'
    H_SLIDESHOW_CONTENT_TOOLBAR_ACTIONS_END = 'h_slideshow_toolbar_actions_end'
    H_SLIDESHOW_CONTENT_CSS = 'h_slideshow_css'
    H_SLIDESHOW_CONTENT_JAVASCRIPT = 'h_slideshow_javascript'

    H_SYSINFO_TOOLBAR_ACTIONS_START = 'h_sysinfo_toolbar_actions_start'
    H_SYSINFO_TOOLBAR_ACTIONS_END = 'h_sysinfo_toolbar_actions_end'

    H_PLAYLIST_TOOLBAR_ACTIONS_START = 'h_playlist_toolbar_actions_start'
    H_PLAYLIST_TOOLBAR_ACTIONS_END = 'h_playlist_toolbar_actions_end'
    H_PLAYLIST_CSS = 'h_playlist_css'
    H_PLAYLIST_JAVASCRIPT = 'h_playlist_javascript'

    H_ROOT_CSS = 'h_root_css'
    H_ROOT_JAVASCRIPT = 'h_root_javascript'
    H_ROOT_NAV_ELEMENT_START = 'h_root_nav_element_start'
    H_ROOT_NAV_ELEMENT_END = 'h_root_nav_element_end'
    H_ROOT_PILL_ELEMENT_START = 'h_root_pill_element_start'
    H_ROOT_PILL_ELEMENT_END = 'h_root_pill_element_end'
    H_ROOT_FOOTER = 'h_root_footer'
