from vitessce import (
    VitessceConfig,
    CoordinationLevel as CL,
    SpatialDataWrapper,
    get_initial_coordination_scope_prefix,
)
import warnings
import os
import utils
import json

# env vars; defined as docker vars
SPATIALDATA_URI = "http://localhost:80/data/zarr"
CONFIG_PATH = os.environ.get("CONFIG_PATH", "")
if CONFIG_PATH == "":
    CONFIG_PATH = "../"
CS = "um_aligned_ltb12_grid" 

# cmaps
CELL_TYPE_SPECS = {
    "Immune": {
        "_color": "#2356FF",
        "B cell": {
            "_color": "#4682B4",
            "B cell": "#4682B4",
            "B cell dividing": "#2E57B1"
        },
        "DC": {
            "_color": "#9370DB",
            "cDC1": "#AD9BD3",
            "cDC2": "#9370DB",
            "pDC": "#A742DA",
            "DC mature": "#6126D7"
        },
        "Macrophage": {
            "_color": "#D2B48C",
            "Macrophage": "#D2B48C",
            "Macrophage alveolar": "#D2903A",
        } ,
        "Mast": "#2F4F4F",
        "Monocyte": {
            "_color": "#8B4513",
            "Monocyte classical": "#8B4513",
            "Monocyte non-classical": "#8B2713" 
        },
        "Myeloid dividing": "#696969",
        "Neutrophils": "#708090",
        "Plasma": "#00BFFF",
        "T cell": {
            "_color":"#FFA500",
            "T cell CD4": "#FFA500",
            "T cell dividing": "#FBB431",
            "T cell regulatory": "#FF6A00",
            "T cell CD8": "#D4FF00",
        }
    },
    "Endothelial": "#90EE90",
    "Stromal": {
        "_color": "#644300",
        "Fibroblast": "#006400",
        "Pericyte": "#ADD8E6",
        "Smooth muscle cell": "#D8BFD8"
    },
    "Tumor": "#FF4500",
}

NICHE_SPECS = {
    "n1": "#8CC084",
    "n2": "#b6e7e0",
    "n3": "#d85a44",
    "n4": "#2e92a2",
    "n5": "#aa3f5d",
    "n6": "#ffb651"
}

LTB12_SPECS = {
    "No": "#792357",
    "Yes": "#374937"
}

ALL_SPECS = {
    "Cell Type": CELL_TYPE_SPECS,
    "Niche": NICHE_SPECS,
    "LTB12": LTB12_SPECS
}

PATH_SPECS = {
    "Pathology Annotation": {
        "Tumor Cells": "#DD5172",
        "Stroma":      "#8EAD50",
        "Background": "#638EA3",
        "Blood vessel": "#557296",
        "Immune Cells": "#FAC246",
        "Necrosis": "#2E2A31",
    }
}


def build_config() -> VitessceConfig:
    warnings.filterwarnings("ignore")

    vc = VitessceConfig(schema_version="1.0.18", name="NSCLC Spatial Atlas Mini")
    dataset = vc.add_dataset(name="YTMA709", uid="YTMA709")
    # H&E image + pathology shape segmentations  (obsType: "path")
    he_obj = SpatialDataWrapper(
        sdata_url=SPATIALDATA_URI,
        image_path="images/HE_mosaic",
        obs_segmentations_path="shapes/pathology_mosaic",
        obs_set_paths=["tables/pathology_mosaic_table/obs/classification"],
        obs_set_names=["Pathology Annotation"],
        table_path="tables/pathology_mosaic_table",
        coordinate_system=CS,
        coordination_values={
            "fileUid": "he",
            "obsType": "PathologyAnnotation",
        },
    )
    dataset.add_object(he_obj)

    # CosMX image + cell segmentations  (obsType: "cell")
    cosmx_obj = SpatialDataWrapper(
        sdata_url=SPATIALDATA_URI,
        image_path="images/fov_mosaic",
        obs_segmentations_path="labels/labels_mosaic",
        obs_embedding_paths=[
            "tables/table/obsm/UMAP",
            "tables/table/obsm/PCA"
        ],
        obs_embedding_names=["UMAP", "PCA"],
        obs_feature_matrix_path="tables/table/layers/logcounts",
        obs_labels_paths=["tables/table/obs/cell_type"],   # ← tooltip content
        obs_labels_names=["Cell Type"],
        obs_set_paths=[
            [
                "tables/table/obs/cell_types_L0", 
                "tables/table/obs/cell_types_L1", 
                "tables/table/obs/cell_type"
            ],
            "tables/table/obs/Niche",
            "tables/table/obs/LTB12"
        ],
        obs_set_names=["Cell Type", "Niche", "LTB12"],
        coordinate_system=CS,
        coordination_values={
            "fileUid": "fov",
            "obsType": "cell",
            "sampleType": "fov",
            "featureType": "gene",
            "featureValueType": "expression"
        },
        table_path="tables/table"
    )
    dataset.add_object(cosmx_obj)

    spatial = vc.add_view("spatialBeta", dataset=dataset)
    feature_list = vc.add_view("featureList", dataset=dataset)
    umap_scatter = vc.add_view("scatterplot", dataset=dataset, mapping="UMAP")
    pca_scatter = vc.add_view("scatterplot", dataset=dataset, mapping="PCA")
    # heatmap = vc.add_view("heatmap", dataset=dataset)
    layer_controller = vc.add_view("layerControllerBeta", dataset=dataset)
    cell_obs_sets = vc.add_view("obsSets", dataset=dataset)
    path_obs_sets = vc.add_view("obsSets", dataset=dataset)

    [obs_color_encoding_scope]  = vc.add_coordination("obsColorEncoding")
    obs_color_encoding_scope.set_value("cellSetSelection")

    [cell_color_scope]     = vc.add_coordination("obsSetColor")
    [cell_selection_scope] = vc.add_coordination("obsSetSelection")
    [cell_obs_highlight_scope] = vc.add_coordination("obsHighlight")
    cell_obs_highlight_scope.set_value(None)

    # Separate scopes between the pathology and cell annots
    [path_color_encoding_scope] = vc.add_coordination("obsColorEncoding")
    path_color_encoding_scope.set_value("cellSetSelection")
    [path_obs_highlight_scope] = vc.add_coordination("obsHighlight")
    path_obs_highlight_scope.set_value(None)

    [path_color_scope]     = vc.add_coordination("obsSetColor")
    [path_selection_scope] = vc.add_coordination("obsSetSelection")
    [path_stroke_fill_scope] = vc.add_coordination("spatialSegmentationFilled")
    [path_stroke_width_scope] = vc.add_coordination("spatialSegmentationStrokeWidth")
    
    # Image layer coordination
    vc.link_views_by_dict(
        [spatial, layer_controller],
        {
            "imageLayer": CL(
                [
                    {
                        "fileUid": "he",
                        "obsType": "HE",
                        "photometricInterpretation": "RGB",
                        "spatialLayerVisible": True,
                        "spatialLayerOpacity": 1.0,
                    },
                    {
                        "fileUid": "fov",
                        "photometricInterpretation": "RGB",
                        "spatialLayerTransparentColor": [0, 0, 1], # sentinel value for interfov sparse val
                        "spatialLayerVisible": True,
                        "spatialLayerOpacity": 1.0, 
                    },
                ]
            )
        },
        scope_prefix=get_initial_coordination_scope_prefix("YTMA709", "image"),
    )

    # Segmentation layer coordination
    vc.link_views_by_dict(
        [spatial, layer_controller],
        {
            "segmentationLayer": CL([
                {
                    "fileUid": "fov",
                    "segmentationChannel": CL([{
                        "obsType": "cell",
                        "obsColorEncoding":  obs_color_encoding_scope,
                        "obsSetColor":       cell_color_scope,
                        "obsSetSelection":   cell_selection_scope,
                        "obsHighlight": cell_obs_highlight_scope
                    }])
                },
                {
                    "fileUid": "he",
                    "segmentationChannel": CL([{
                        "obsType": "PathologyAnnotation",
                        "obsColorEncoding":  path_color_encoding_scope,
                        "obsSetColor":       path_color_scope,
                        "obsSetSelection":   path_selection_scope,
                        "obsHighlight": path_obs_highlight_scope,
                        "spatialSegmentationFilled": path_stroke_fill_scope,
                        "spatialSegmentationStrokeWidth": path_stroke_width_scope
                    }])
                },
            ])
        },
        scope_prefix=get_initial_coordination_scope_prefix("YTMA709", "obsSegmentations"),
    )

    vc.link_views(
        [
            spatial, layer_controller, feature_list, cell_obs_sets, umap_scatter, pca_scatter, 
            # heatmap
        ],
        ["obsType"],
        [cosmx_obj.obs_type_label],
    )
    vc.link_views([path_obs_sets], ["obsType"], ["PathologyAnnotation"])
    vc.link_views_by_dict([feature_list, cell_obs_sets], {
        "obsColorEncoding": obs_color_encoding_scope,
    }, meta=False)
    vc.link_views_by_dict([path_obs_sets], {
        "obsColorEncoding": path_color_encoding_scope,
    }, meta=False)

    cell_color_scope.set_value(utils.make_all_obs_set_colors(ALL_SPECS))
    cell_selection_scope.set_value(utils.make_all_obs_set_selection(ALL_SPECS, include=["Cell Type"]))
    path_color_scope.set_value(utils.make_all_obs_set_colors(PATH_SPECS))
    path_selection_scope.set_value(utils.make_all_obs_set_selection(PATH_SPECS))
    path_stroke_fill_scope.set_value(False)
    path_stroke_width_scope.set_value(8.0)
    
    vc.link_views_by_dict(
        [
            cell_obs_sets, umap_scatter, pca_scatter, 
            # heatmap
        ], {
            "obsSetColor":     cell_color_scope,
            "obsSetSelection": cell_selection_scope,
            "obsHighlight": cell_obs_highlight_scope
        }, meta=False)

    vc.link_views_by_dict(
        [
            spatial, layer_controller, cell_obs_sets, umap_scatter, pca_scatter, 
            # heatmap
        ], {
            "obsHighlight": cell_obs_highlight_scope,
        }, meta=False)

    vc.link_views_by_dict([path_obs_sets], {
        "obsSetColor":     path_color_scope,
        "obsSetSelection": path_selection_scope,
        "obsHighlight": path_obs_highlight_scope
    }, meta=False)
    vc.link_views_by_dict([spatial, layer_controller], {}, meta=True)
    vc.layout(
        (spatial | (layer_controller / feature_list | (path_obs_sets / cell_obs_sets)))
        / (
            (umap_scatter | pca_scatter) 
            # / heatmap
        )
    )

    return vc

def main():
    vc = build_config() 
    with open(f"{CONFIG_PATH}/config.json", "w") as f:
        json.dump(vc.to_dict(), f, indent=2)

if __name__ == "__main__":
    main()