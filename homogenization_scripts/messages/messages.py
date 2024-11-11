from .main_script.main_script_messages import Main
from .reuse_results.reuse_results_messages import Reuse
from .elastic_tensor_fitting.elastic_tensor_fitting import ElasticTensor
from .yield_surface.yield_surface import YieldSurface

class Messages:
    Main: Main
    Reuse: Reuse
    ElasticTensor: ElasticTensor
    YieldSurface: YieldSurface
    pass

Messages.Main = Main()
Messages.Reuse = Reuse()
Messages.ElasticTensor = ElasticTensor()
Messages.YieldSurface = YieldSurface()