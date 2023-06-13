from . import procedure,query

#info
forums = query.forum_names
boards = query.board_names
threads = query.get_threads
posts = query.get_posts

#add new
add_forum = procedure.add_forum
add_board = procedure.add_board
add_thread = procedure.add_thread
add_post = procedure.add_post

#change_access
set_forum_access = procedure.set_forum_access
set_board_access = procedure.set_board_access
set_thread_access = procedure.set_thread_access

#edit
edit_post = procedure.edit_post