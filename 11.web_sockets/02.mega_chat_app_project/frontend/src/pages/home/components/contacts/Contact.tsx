import "./Main.css"
import { defaultProfilePicture } from "../../../../utils/core"
import { useSelector } from "react-redux"
import { useNavigate, useParams } from "react-router-dom"

const Contact = ({ user }: any) => {

    const currentUser = useSelector((state: any) => state?.user)
    const navigate = useNavigate()
    const { userId } = useParams()

    return (
        <>
            <div className={`contact ${userId === user?.id ? "active-contact" : ""}`} onClick={() => navigate(`/chat/${user?.id}`)}>
                <img src={user?.profilePhoto ? user?.profilePhoto : defaultProfilePicture} alt="profile photo"
                    onError={(e: any) => e.target.src = defaultProfilePicture}
                />
                <p>
                    {
                        currentUser?.id === user?.id ? "You" :
                            user?.username ? user?.username : ""
                    }
                </p>
            </div>
        </>
    )
}

export default Contact