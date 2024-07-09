from .analysis_tools import *
import atexit
import readline

def interactive_startup(histfile):
    readline.parse_and_bind('tab: complete')
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass

isotope=""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        isotope = sys.argv[1]
        histfile = f"SessionLog_{isotope}.py"
        readline.clear_history()

        interactive_startup(histfile)

        def save_history(histfile):
            readline.write_history_file(histfile)

        atexit.register(save_history, histfile)
    else:
        isotope = '27F'
else:
    try:
        isotope=os.environ["E19044Isotope"]
    except:
        isotope = "29F"

if __name__ == "__main__":
    chain, log, data_dir, files = prep_chain(isotope)
    can = prep_canvas()




