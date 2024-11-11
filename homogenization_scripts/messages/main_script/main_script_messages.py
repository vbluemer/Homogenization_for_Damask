class Main:
    class Banners:

        def start_pre_process():
            print("""
###############################################################################
########################### Starting pre-processing ########################### 
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
""")
            
        def start_simulations():
            print("""
###############################################################################
############################ Starting simulations ############################# 
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
""")

        def simulations_completed():
            print("""
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
############################ Simulations completed ############################ 
###############################################################################
""")

        def start_post_processing() -> None:
            print("""
###############################################################################
########################## Starting post-processing ########################### 
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
""")
            
        def post_processing_completed() -> None:
            print("""
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
########################## Post-processing completed ##########################
###############################################################################
""")
    
        def normal_end_of_script():
            print("""
###############################################################################
##################### The script has completed it's tasks #####################
###############################################################################
""")

    def user_did_not_run_queued_jobs(self) -> None:
        print("Stopping...")