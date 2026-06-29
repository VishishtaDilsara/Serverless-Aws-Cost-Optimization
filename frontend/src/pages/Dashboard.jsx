import React, { useState } from "react";

const Dashboard = () => {
  const [data, setData] = useState([]);
  const handleFetchData = () => {
    // Fetch data logic here
    const res = fetch(
      "https://rj9p9roj.execute-api.ap-south-1.amazonaws.com/dev/recommendations"
    )
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setData(data);
      });
  };

  const handleCloseIssue = (index) => {
    const updatedData = [...data];
    updatedData[index].Status = "Closed";
    setData(updatedData);

    // Optionally, send a POST request to update status on backend
    fetch(
      "https://rj9p9roj.execute-api.ap-south-1.amazonaws.com/dev/update-status",
      {
        method: "POST",
        // headers: {
        //   "Content-Type": "application/json",
        // },
        body: JSON.stringify({
          ResourceId: data[index].ResourceId,
          Issue: data[index].Issue,
          Status: "Closed",
        }),
      }
    );
  };

  const handleAction = async (index) => {
    // Implement action logic here
     const res = await fetch(
    "https://rj9p9roj.execute-api.ap-south-1.amazonaws.com/dev/action",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ResourceId: data[index].ResourceId,
        Issue: data[index].Issue,
        Action: data[index].Issue === "Idle Instance" ? "stop" : "delete",
        Service: data[index].Service,
      }),
    }
  );

  const result = await res.json();
  console.log(result);
    alert(`Action taken on ${data[index].ResourceId}`);
  }

  //   const [data, setData] = useState([
  //     {
  //       ResourceId: "vol-0123456789abcdef0",
  //       Service: "EBS",
  //       Issue: "Unattached Volume",
  //       Recommendation: "Delete if not needed",
  //       EstimatedSavings: "50 GB storage/month",
  //       Status: "Open",
  //     },
  //     {
  //       ResourceId: "vol-0fedcba9876543210",
  //       Service: "EBS",
  //       Issue: "gp2 Volume",
  //       Recommendation: "Migrate to gp3",
  //       EstimatedSavings: "Up to 20% lower cost",
  //       Status: "Open",
  //     },
  //     {
  //       ResourceId: "snap-0123abcd4567efgh8",
  //       Service: "EBS",
  //       Issue: "Old Snapshot",
  //       Recommendation: "Review/Delete snapshot older than 30 days",
  //       EstimatedSavings: "100 GB storage/month",
  //       Status: "Open",
  //     },
  //     {
  //       ResourceId: "i-0abcdef1234567890",
  //       Service: "EC2",
  //       Issue: "Idle Instance",
  //       Recommendation: "Stop or downsize instance",
  //       EstimatedSavings: "$25/month",
  //       Status: "Open",
  //     },
  //     {
  //       ResourceId: "i-0abcdef9876543210",
  //       Service: "EC2",
  //       Issue: "Low CPU Utilization",
  //       Recommendation: "Consider smaller instance type",
  //       EstimatedSavings: "$15/month",
  //       Status: "Closed",
  //     },
  //   ]);
  console.log(data);
  const [search, setSearch] = useState("");

  const filteredData = data.filter(
    (item) =>
      item.ResourceId.toLowerCase().includes(search.toLowerCase()) ||
      item.Service.toLowerCase().includes(search.toLowerCase()) ||
      item.Issue.toLowerCase().includes(search.toLowerCase()) ||
      item.Recommendation.toLowerCase().includes(search.toLowerCase()) ||
      item.Status.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div>
        <h2 className="text-4xl font-bold flex justify-center m-5">
          Dashboard Page
        </h2>
      </div>
      <div className="flex justify-center m-4">
        <div className="flex justify-center m-4">
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="p-2 border rounded-xl w-80"
          />
        </div>
        <div className="flex justify-center m-4">
          <button
            onClick={handleFetchData}
            className="cursor-pointer px-2 rounded-xl bg-amber-200 border h-10 text-xl font-bold"
          >
            Fetch Data
          </button>
        </div>
      </div>
      <div>
        {filteredData &&
          filteredData.map((item, index) => (
            <div
              key={index}
              className="max-w-md mx-auto bg-amber-50 hover:shadow-2xl hover:shadow-amber-200 rounded-xl overflow-hidden md:max-w-2xl my-4"
            >
              <div className="p-4 space-y-1">
                <div className="flex justify-end">
                  <h2 className="px-1 bg-orange-300 border w-10 rounded-lg font-bold">
                    {item.Service}
                  </h2>
                </div>
                <h2 className="text-xl font-bold text-red-400">{item.Issue}</h2>
                <p className="font-bold">
                  ResourceId:{" "}
                  <span className="text-gray-600 font-medium">
                    {item.ResourceId}
                  </span>
                </p>
                <p className="font-bold">
                  Recommendation:{" "}
                  <span className="text-gray-600 font-medium">
                    {item.Recommendation}
                  </span>
                </p>
                <p className="font-bold">
                  Estimated Savings:{" "}
                  <span className="text-gray-600 font-medium">
                    {item.EstimatedSavings}
                  </span>
                </p>
                <p className="font-bold">
                  Status:{" "}
                  <span className="text-gray-600 font-medium">
                    {item.Status}
                  </span>
                </p>

                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => handleCloseIssue(index)}
                    className="cursor-pointer p-1 rounded-2xl bg-amber-200 border font-bold"
                  >
                    Close Issue
                  </button>
                  <button
                    onClick={() => handleAction(index)}
                    className="cursor-pointer p-1 rounded-2xl bg-amber-200 border font-bold"
                  >
                    Take Action
                  </button>
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};

export default Dashboard;
