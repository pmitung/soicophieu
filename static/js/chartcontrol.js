
function select1w() {
    console.log("ok");
    if (labels.length >= 8) {
        updatedLabels = labels.slice(labels.length - 8, labels.length);
        updatedData = datapoints.slice(labels.length - 8, labels.length);
        newChart.config.data.labels = updatedLabels;
        newChart.config.data.datasets[0].data = updatedData;
        newChart.update();

        updatedLabelsVolumn = labels_volumn.slice(labels_volumn.length - 8, labels_volumn.length);
        updatedVolumn = datapoints_volumn.slice(labels_volumn.length - 8, labels_volumn.length);
        newvolumnChart.config.data.labels = updatedLabelsVolumn;
        newvolumnChart.config.data.datasets[0].data = updatedVolumn;
        newvolumnChart.update();

        updatedLabelsView = labels_viewchart.slice(labels_viewchart.length - 8, labels_viewchart.length);
        updatedView = datapoints_viewchart.slice(labels_viewchart.length - 8, labels_viewchart.length);
        newviewChart.config.data.labels = updatedLabelsView;
        newviewChart.config.data.datasets[0].data = updatedView;
        newviewChart.update();
    } else {
        newChart.config.data.labels = labels;
        newChart.config.data.datasets[0].data = datapoints;
        newChart.update();

        newvolumnChart.config.data.labels = labels_volumn;
        newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
        newvolumnChart.update();

        newviewChart.config.data.labels = labels_viewchart;
        newviewChart.config.data.datasets[0].data = datapoints_viewchart;
        newviewChart.update();
    }
};

function select1m() {
    if (labels.length >= 31) {
        updatedLabels = labels.slice(labels.length - 31, labels.length);
        updatedData = datapoints.slice(labels.length - 31, labels.length);
        newChart.config.data.labels = updatedLabels;
        newChart.config.data.datasets[0].data = updatedData;
        newChart.update();

        updatedLabelsVolumn = labels_volumn.slice(labels_volumn.length - 31, labels_volumn.length);
        updatedVolumn = datapoints_volumn.slice(labels_volumn.length - 31, labels_volumn.length);
        newvolumnChart.config.data.labels = updatedLabelsVolumn;
        newvolumnChart.config.data.datasets[0].data = updatedVolumn;
        newvolumnChart.update();

        updatedLabelsView = labels_viewchart.slice(labels_viewchart.length - 31, labels_viewchart.length);
        updatedView = datapoints_viewchart.slice(labels_viewchart.length - 31, labels_viewchart.length);
        newviewChart.config.data.labels = updatedLabelsView;
        newviewChart.config.data.datasets[0].data = updatedView;
        newviewChart.update();
    } else {
        newChart.config.data.labels = labels;
        newChart.config.data.datasets[0].data = datapoints;
        newChart.update();

        newvolumnChart.config.data.labels = labels_volumn;
        newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
        newvolumnChart.update();

        newviewChart.config.data.labels = labels_viewchart;
        newviewChart.config.data.datasets[0].data = datapoints_viewchart;
        newviewChart.update();
    }
};

function select3m() {
    if (labels.length >= 91) {
        updatedLabels = labels.slice(labels.length - 91, labels.length);
        updatedData = datapoints.slice(labels.length - 91, labels.length);
        newChart.config.data.labels = updatedLabels;
        newChart.config.data.datasets[0].data = updatedData;
        newChart.update();

        updatedLabelsVolumn = labels_volumn.slice(labels_volumn.length - 91, labels_volumn.length);
        updatedVolumn = datapoints_volumn.slice(labels_volumn.length - 91, labels_volumn.length);
        newvolumnChart.config.data.labels = updatedLabelsVolumn;
        newvolumnChart.config.data.datasets[0].data = updatedVolumn;
        newvolumnChart.update();

        updatedLabelsView = labels_viewchart.slice(labels_viewchart.length - 91, labels_viewchart.length);
        updatedView = datapoints_viewchart.slice(labels_viewchart.length - 91, labels_viewchart.length);
        newviewChart.config.data.labels = updatedLabelsView;
        newviewChart.config.data.datasets[0].data = updatedView;
        newviewChart.update();
    } else {
        newChart.config.data.labels = labels;
        newChart.config.data.datasets[0].data = datapoints;
        newChart.update();

        newvolumnChart.config.data.labels = labels_volumn;
        newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
        newvolumnChart.update();
        
        newviewChart.config.data.labels = labels_viewchart;
        newviewChart.config.data.datasets[0].data = datapoints_viewchart;
        newviewChart.update();
    }
};

function select6m() {
    if (labels.length >= 181) {
        updatedLabels = labels.slice(labels.length - 181, labels.length);
        updatedData = datapoints.slice(labels.length - 181, labels.length);
        newChart.config.data.labels = updatedLabels;
        newChart.config.data.datasets[0].data = updatedData;
        newChart.update();

        updatedLabelsVolumn = labels_volumn.slice(labels_volumn.length - 181, labels_volumn.length);
        updatedVolumn = datapoints_volumn.slice(labels_volumn.length - 181, labels_volumn.length);
        newvolumnChart.config.data.labels = updatedLabelsVolumn;
        newvolumnChart.config.data.datasets[0].data = updatedVolumn;
        newvolumnChart.update();

        updatedLabelsView = labels_viewchart.slice(labels_viewchart.length - 181, labels_viewchart.length);
        updatedView = datapoints_viewchart.slice(labels_viewchart.length - 181, labels_viewchart.length);
        newviewChart.config.data.labels = updatedLabelsView;
        newviewChart.config.data.datasets[0].data = updatedView;
        newviewChart.update();
    } else {
        newChart.config.data.labels = labels;
        newChart.config.data.datasets[0].data = datapoints;
        newChart.update();

        newvolumnChart.config.data.labels = labels_volumn;
        newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
        newvolumnChart.update();

        newviewChart.config.data.labels = labels_viewchart;
        newviewChart.config.data.datasets[0].data = datapoints_viewchart;
        newviewChart.update();
    }
};

function select1y() {
    if (labels.length >= 366) {
        updatedLabels = labels.slice(labels.length - 366, labels.length);
        updatedData = datapoints.slice(labels.length - 366, labels.length);
        newChart.config.data.labels = updatedLabels;
        newChart.config.data.datasets[0].data = updatedData;
        newChart.update();

        updatedLabelsVolumn = labels_volumn.slice(labels_volumn.length - 366, labels_volumn.length);
        updatedVolumn = datapoints_volumn.slice(labels_volumn.length - 366, labels_volumn.length);
        newvolumnChart.config.data.labels = updatedLabelsVolumn;
        newvolumnChart.config.data.datasets[0].data = updatedVolumn;
        newvolumnChart.update();

        updatedLabelsView = labels_viewchart.slice(labels_viewchart.length - 366, labels_viewchart.length);
        updatedView = datapoints_viewchart.slice(labels_viewchart.length - 366, labels_viewchart.length);
        newviewChart.config.data.labels = updatedLabelsView;
        newviewChart.config.data.datasets[0].data = updatedView;
        newviewChart.update();
    } else {
        newChart.config.data.labels = labels;
        newChart.config.data.datasets[0].data = datapoints;
        newChart.update();

        newvolumnChart.config.data.labels = labels_volumn;
        newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
        newvolumnChart.update();

        newviewChart.config.data.labels = labels_viewchart;
        newviewChart.config.data.datasets[0].data = datapoints_viewchart;
        newviewChart.update();
    }  
};

function select5y() {
    if (labels.length >= (365*5+1)) {
        updatedLabels = labels.slice(labels.length - 365*5 - 1, labels.length);
        updatedData = datapoints.slice(labels.length - 365*5 - 1, labels.length);
        newChart.config.data.labels = updatedLabels;
        newChart.config.data.datasets[0].data = updatedData;
        newChart.update();

        updatedLabelsVolumn = labels_volumn.slice(labels_volumn.length - 365*5 - 1, labels_volumn.length);
        updatedVolumn = datapoints_volumn.slice(labels_volumn.length - 365*5 - 1, labels_volumn.length);
        newvolumnChart.config.data.labels = updatedLabelsVolumn;
        newvolumnChart.config.data.datasets[0].data = updatedVolumn;
        newvolumnChart.update();

        updatedLabelsView = labels_viewchart.slice(labels_viewchart.length - 365*5 - 1, labels_viewchart.length);
        updatedView = datapoints_viewchart.slice(labels_viewchart.length - 365*5 - 1, labels_viewchart.length);
        newviewChart.config.data.labels = updatedLabelsView;
        newviewChart.config.data.datasets[0].data = updatedView;
        newviewChart.update();
    } else {
        newChart.config.data.labels = labels;
        newChart.config.data.datasets[0].data = datapoints;
        newChart.update();

        newvolumnChart.config.data.labels = labels_volumn;
        newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
        newvolumnChart.update();

        newviewChart.config.data.labels = labels_viewchart;
        newviewChart.config.data.datasets[0].data = datapoints_viewchart;
        newviewChart.update();
    }
};

function selectAll() {
    newChart.config.data.labels = labels;
    newChart.config.data.datasets[0].data = datapoints;
    newChart.update();

    newvolumnChart.config.data.labels = labels_volumn;
    newvolumnChart.config.data.datasets[0].data = datapoints_volumn;
    newvolumnChart.update();

    newviewChart.config.data.labels = labels_viewchart;
    newviewChart.config.data.datasets[0].data = datapoints_viewchart;
    newviewChart.update();
}