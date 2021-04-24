const renderChart2 = (data, labels) => {
    var ctx = document.getElementById("myChart2").getContext("2d");
    var myChart2 = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [
          {
            label: "Last 6 months income",
            data: data,
            backgroundColor: [
              "rgba(255, 99, 132, 0.2)",
              "rgba(54, 162, 235, 0.2)",
              "rgba(255, 206, 86, 0.2)",
              "rgba(75, 192, 192, 0.2)",
              "rgba(153, 102, 255, 0.2)",
              "rgba(255, 159, 64, 0.2)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
              "rgba(255, 159, 64, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        title: {
          display: true,
          text: "Income in the last 6 months",
        },
      },
    });
  };
  
  const getChartIncomeData = () => {
    console.log("fetching");
    fetch("/income_summary")
      .then((res) => res.json())
      .then((results) => {
        console.log("results", results);
        const income_data = results.income_data;
        const [labels, data] = [
          Object.keys(income_data),
          Object.values(income_data),
        ];
  
        renderChart2(data, labels);
      });
  };
  
  document.onload = getChartIncomeData();